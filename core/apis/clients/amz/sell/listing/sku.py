from .base import AmzSpApiListingBaseFetcher
import pandas as pd
from sp_api.base.marketplaces import Marketplaces
from core.utils.main import get_rate_limiter
from concurrent.futures import ThreadPoolExecutor
from sp_api.base.exceptions import (
    SellingApiRequestThrottledException,
    SellingApiNotFoundException,
)
import asyncio
import time
from asgiref.sync import sync_to_async


class AmzSkuFetcher(AmzSpApiListingBaseFetcher):
    def __init__(self, marketplace: Marketplaces, *args, **kwargs):
        super().__init__(marketplace, *args, **kwargs)

    async def get_sale_price(self, sku_names: list | None = None) -> pd.DataFrame:
        from kn_api._kn_sp_api.products import Products
        from django.core.paginator import Paginator
        from core.models.amz import AmzSku

        if sku_names is None:
            sku_names = await sync_to_async(list)(
                AmzSku.objects.all().values_list("name", flat=True)
            )

        def get_failed_list(data):
            failed_list = []
            for i in data:
                if isinstance(i, list):
                    failed_list.append(i)
            return failed_list

        async def get_product_by_sku(
            sku_limiter, product_client: Products, sku_list, MarketplaceId
        ):
            async with sku_limiter:
                try:
                    with ThreadPoolExecutor() as executor:
                        loop = asyncio.get_event_loop()
                        data = await loop.run_in_executor(
                            executor,
                            lambda: product_client.get_product_pricing_for_skus(
                                seller_sku_list=sku_list, MarketplaceId=MarketplaceId
                            ),
                        )
                except SellingApiRequestThrottledException:
                    return sku_list
                else:
                    return data

        paginator = Paginator(sku_names, 20)  # Create a Paginator object
        sku_lists = list()
        for page_number in paginator.page_range:
            # Get the skus for the current page
            page_skus = paginator.page(page_number)
            sku_lists.append([sku for sku in page_skus])

        if sku_lists:

            product_client = Products(marketplace=Marketplaces.IN)
            MarketplaceId = Marketplaces.IN.marketplace_id

            async def init_loop(sku_limiter, sku_lists):
                sku_tasks = [
                    asyncio.create_task(
                        get_product_by_sku(
                            sku_limiter, product_client, sku_list, MarketplaceId
                        )
                    )
                    for sku_list in sku_lists
                ]
                sku_results = await asyncio.gather(*sku_tasks)

                return sku_results

            sku_limiter = get_rate_limiter(
                15, 15
            )  # Experimental, sometimes work and give fast response

            sku_results = await init_loop(sku_limiter, sku_lists)
            final_data = sku_results.copy()
            final_data = [
                i for i in final_data if not isinstance(i, list)
            ]  # Filtered out failed skus
            failed_count = len(get_failed_list(sku_results))
            if failed_count:
                sku_limiter = get_rate_limiter(1, 0.5)  # As per documentation
                MAX_RETRY = 50
                for _ in range(MAX_RETRY):  # MAX_RETRY times
                    print(
                        f"Retrying failed skus: Retry Count: {_+1} | Failed Count: {failed_count}"
                    )
                    failed_skus = get_failed_list(sku_results)
                    sku_results = await init_loop(sku_limiter, failed_skus)
                    success_retry = [
                        i for i in sku_results if not isinstance(i, list)]
                    final_data.extend(success_retry)
                    failed_count = len(get_failed_list(sku_results))
                    if not failed_count:
                        break
                    # 0.5 Requests per second
                    time.sleep((failed_count / 0.5) + _)
                else:
                    list_fail = get_failed_list(sku_results)
                    total_fail = len(list_fail)
                    print(
                        f"Some skus failed after {MAX_RETRY} retries.\nFailed Count: {total_fail}\nSKU: {list_fail}"
                    )

            pass_count = 0
            for res in final_data:
                if not isinstance(res, list):
                    pass_count += len(res.payload)
            print(f"Pass: {pass_count}")
            df_list = [["name", "asin", "sale_price"]]
            # Create a DataFrame
            for i in final_data:
                for j in i.payload:
                    if j["status"] == "Success":
                        if j["Product"].get("Offers", False):
                            df_list.append(
                                [
                                    j["Product"]["Identifiers"]["SKUIdentifier"][
                                        "SellerSKU"
                                    ],
                                    j["Product"]["Identifiers"]["MarketplaceASIN"][
                                        "ASIN"
                                    ],
                                    j["Product"]["Offers"][0]["BuyingPrice"][
                                        "ListingPrice"
                                    ]["Amount"],
                                ]
                            )
            df = pd.DataFrame(df_list[1:], columns=df_list[0])
            return df

    async def get_product_type(self, sku_names: list | None = None) -> pd.DataFrame:
        from core.models.amz import AmzSku

        if sku_names is None:
            sku_names = await sync_to_async(list)(
                AmzSku.objects.all().values_list("name", flat=True)
            )

        def filter_failed(get_results):
            return [i[0] for i in get_results if isinstance(i, list) and i[1] is None]

        sellerId = "A1U16T1MFHGN7V"
        limiter_get = get_rate_limiter(10, 5)

        async def init_sku_get(sku_name):
            async with limiter_get:
                try:
                    with ThreadPoolExecutor() as executor:
                        loop = asyncio.get_event_loop()
                        data = await loop.run_in_executor(
                            executor,
                            lambda: self.client.get_listings_item(
                                sellerId=sellerId, sku=sku_name
                            ),
                        )
                    product_type = data.payload["summaries"][0]["productType"]
                except SellingApiRequestThrottledException:
                    print(f"Failed GET request for {sku_name}: Throttled")
                    return [sku_name, None]
                except SellingApiNotFoundException as e:
                    print(f"Failed GET request for {sku_name}: Not Found {e}")
                    return None
                print(f"Success GET request for {sku_name}: {product_type}")
                return [sku_name, product_type]

        get_tasks = []
        for sku_name in sku_names:
            get_tasks.append(asyncio.create_task(init_sku_get(sku_name)))
        get_results = await asyncio.gather(*get_tasks)
        retry_get = filter_failed(get_results)
        for _ in range(5):  # Retry 5 times
            if not retry_get:
                break
            print(
                f"Retrying failed skus: Retry Count: {_+1} | Failed Count: {len(retry_get)}"
            )
            get_tasks = []
            for sku_name in retry_get:
                get_tasks.append(asyncio.create_task(init_sku_get(sku_name)))
            retry_results = await asyncio.gather(*get_tasks)
            get_results.extend(
                [i for i in retry_results if isinstance(
                    i, list) and i[1] is not None]
            )
            retry_get = filter_failed(retry_results)
        else:
            print(f"Some skus failed after 5 retries. {retry_get}")

        get_results = [
            i for i in get_results if isinstance(i, list) and i[1] is not None
        ]
        print(
            f"Pass: {len(get_results)} | Failed: {len(sku_names)-len(get_results)}")

        return pd.DataFrame(get_results, columns=["name", "product_type"])

    async def patch_listings_item(self, sku: str, body: dict) -> dict:
        limiter = get_rate_limiter(5, 3)
        async with limiter:
            try:
                with ThreadPoolExecutor() as executor:
                    loop = asyncio.get_event_loop()
                    data = await loop.run_in_executor(
                        executor,
                        lambda: self.client.patch_listings_item(
                            sellerId="A1U16T1MFHGN7V", sku=sku, body=body
                        ),
                    )
            except SellingApiRequestThrottledException:
                print(f"Failed PATCH request for {sku}: Throttled")
                return sku, None
            except SellingApiNotFoundException as e:
                print(f"Failed PATCH request for {sku}: Not Found {e}")
                return sku, None
            print(f"Success PATCH request for {sku}")
            return sku, data.payload

    def publish_sku_price(self, df):
        async def init_loop(df):
            tasks = []
            for i in df.itertuples():
                print(f"Updating price for {i.name}")
                patch_data = {
                    "productType": f"{i.product_type}",
                    "patches": [
                        {
                            "op": "replace",
                            "path": "/attributes/purchasable_offer",
                            "value": [],
                        }
                    ],
                }
                our_price = {
                    "marketplace_id": marketplace_id,
                    "currency": "INR",
                    "our_price": [{"schedule": [{"value_with_tax": ""}]}],
                }
                discounted_price = {
                    "marketplace_id": marketplace_id,
                    "currency": "INR",
                    "discounted_price": [
                        {
                            "schedule": [
                                {"start_at": "", "value_with_tax": "", "end_at": ""}
                            ]
                        }
                    ],
                }
                our_price["our_price"][0]["schedule"][0][
                    "value_with_tax"
                ] = f"{i.our_price}"
                if i.sale_start_at and i.sale_end_at:
                    # Format datetime objects to the specified string format
                    start_dt_formatted = i.sale_start_at.strftime(
                        "%Y-%m-%dT%H:%M:%S.000Z"
                    )
                    end_dt_formatted = i.sale_end_at.strftime(
                        "%Y-%m-%dT%H:%M:%S.000Z"
                    )

                    # Update the dictionary with the formatted datetime strings
                    discounted_price["discounted_price"][0]["schedule"][0][
                        "value_with_tax"
                    ] = f"{i.discounted_price}"
                    discounted_price["discounted_price"][0]["schedule"][0][
                        "start_at"
                    ] = start_dt_formatted
                    discounted_price["discounted_price"][0]["schedule"][0][
                        "end_at"
                    ] = end_dt_formatted
                    patch_data["patches"][0]["value"].append(discounted_price)
                patch_data["patches"][0]["value"].append(our_price)
                tasks.append(
                    asyncio.create_task(
                        self.patch_listings_item(
                            sku=i.name, body=patch_data
                        )
                    )
                )
            results = await asyncio.gather(*tasks)
            fail = [i[0] for i in results if i[1] is None]
            success = [{
                'name': i[0],
                'status': i[1]['status'],
                'submissionId': i[1]['submissionId'] if i[1]['submissionId'] else None,
                'issues': i[1]['issues'] if i[1]['issues'] else None
            } for i in results if i[1] is not None]
            return fail, success
        marketplace_id = self.marketplace.marketplace_id
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        successes = []
        for _ in range(5):
            fail, success = loop.run_until_complete(init_loop(df))
            successes.extend(success)
            if fail:
                print(
                    f"=> Failed to update prices for {fail} SKUs. Retrying after {fail/5} seconds"
                )
                time.sleep(fail / 5)
            else:
                print("=> All prices updated successfully.")
                break
        else:
            print(
                f"Failed to update prices for {fail} SKUs. Please try again later."
            )
        return pd.DataFrame(successes)
