from datetime import datetime, timedelta
from itertools import product
import pandas as pd
from core.services.amz.sell.fetcher.reports.base import AmzSellReportBaseFetcherV3
from kn_api._kn_sp_api.orders import Orders
from sp_api.base.marketplaces import Marketplaces
import asyncio
from sp_api.base.exceptions import (
    SellingApiRequestThrottledException,
    SellingApiNotFoundException,
)
from core.utils.main import get_rate_limiter
from concurrent.futures import ThreadPoolExecutor
import time


class AmzSellReportFetcher(AmzSellReportBaseFetcherV3):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def sales_orders(self, dataStartTime=None, dataEndTime=None):
        report_type = "GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL"
        if dataStartTime is None:
            dataStartTime = datetime.now() - timedelta(days=30)
        if dataEndTime is None:
            dataEndTime = datetime.now()
        data = self.create_report(
            report_type, dataStartTime=dataStartTime, dataEndTime=dataEndTime
        )
        reportId = data.payload["reportId"]
        reportDocumentId = self.fetch_report_by_id(reportId)
        print(f"Report Document Id: {reportDocumentId}")
        data = self.fetch_reports([reportDocumentId])
        return pd.DataFrame(data[1:], columns=data[0])

    def order_settlement(self, createdSince=None, createdUntil=None, **kwargs):
        report_type = "GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE"
        if createdSince is None:
            createdSince = datetime.now() - timedelta(days=14)
        if createdUntil is None:
            createdUntil = datetime.now()
        print(
            f"Fetching Order Settlement Reports Since: {createdSince} to {createdUntil}"
        )
        report_ids = self._fetch_report_ids(
            "reportDocumentId", [report_type], 100, **kwargs
        )
        print(f"Reports To Fetch: {len(report_ids)}")
        data = self.fetch_reports(report_ids)
        return pd.DataFrame(data[1:], columns=data[0])

    def fba_inventory_ledger(self, dataStartTime=None, dataEndTime=None, **kwargs):
        report_type = "GET_LEDGER_SUMMARY_VIEW_DATA"
        if dataStartTime is None:
            dataStartTime = datetime.now() - timedelta(days=14)
        if dataEndTime is None:
            dataEndTime = datetime.now()
        data = self.create_report(
            report_type,
            dataStartTime=dataStartTime,
            dataEndTime=dataEndTime,
            reportOptions={
                "aggregateByLocation": "FC",
                "aggregatedByTimePeriod": "DAILY",
            },
        )
        reportId = data.payload["reportId"]
        reportDocumentId = self.fetch_report_by_id(reportId)
        print(f"Report Document Id: {reportDocumentId}")
        data_list = self.fetch_reports([reportDocumentId])

        def _process_ledger_data(data_list):
            df = pd.DataFrame(data_list[1:], columns=data_list[0])
            df = df.rename(columns=lambda x: x.replace('"', ""))
            df = df.map(lambda value: value.replace('"', ""))
            df["Date"] = pd.to_datetime(df["Date"], format="%m/%d/%Y")
            return df

        processed_df = _process_ledger_data(data_list)
        return processed_df.values.tolist()

    def customer_return(self, dataStartTime=None, dataEndTime=None):
        report_type = "GET_FBA_FULFILLMENT_CUSTOMER_RETURNS_DATA"
        if dataStartTime is None:
            dataStartTime = datetime.now() - timedelta(days=14)
        if dataEndTime is None:
            dataEndTime = datetime.now()
        data = self.create_report(
            report_type, dataStartTime=dataStartTime, dataEndTime=dataEndTime
        )
        reportId = data.payload["reportId"]
        reportDocumentId = self.fetch_report_by_id(reportId)
        print(f"Report Document Id: {reportDocumentId}")
        data = self.fetch_reports([reportDocumentId])
        return pd.DataFrame(data[1:], columns=data[0])

    def removal_shipment(self, dataStartTime=None, dataEndTime=None):
        report_type = "GET_FBA_FULFILLMENT_REMOVAL_SHIPMENT_DETAIL_DATA"
        if dataStartTime is None:
            dataStartTime = datetime.now() - timedelta(days=14)
        if dataEndTime is None:
            dataEndTime = datetime.now()
        data = self.create_report(
            report_type, dataStartTime=dataStartTime, dataEndTime=dataEndTime
        )
        reportId = data.payload["reportId"]
        reportDocumentId = self.fetch_report_by_id(reportId)
        print(f"Report Document Id: {reportDocumentId}")
        data = self.fetch_reports([reportDocumentId])
        return pd.DataFrame(data[1:], columns=data[0])

    def fba_fulfillment_inventory_data(self, createdSince=None, createdUntil=None):
        report_type = "GET_FBA_FULFILLMENT_CURRENT_INVENTORY_DATA"
        if createdSince is None:
            createdSince = datetime.now() - timedelta(days=14)
        if createdUntil is None:
            createdUntil = datetime.now()
        print(f"Fetching FBA Inventory Data Since: {createdSince} to {createdUntil}")
        report_ids = self._fetch_report_ids(
            "reportDocumentId",
            [report_type],
            100,
            createdSince=createdSince,
            createdUntil=createdUntil,
        )
        print(f"Reports To Fetch: {len(report_ids)}")
        data = self.fetch_reports(report_ids)
        columns_to_use = [
            "sku",
            "item-related-fee-amount",
            "price-amount",
            "transaction-type",
            "price-type",
            "item-related-fee-type",
            "quantity-purchased",
            "order-id",
        ]
        return pd.DataFrame(data[1:], columns=data[0])[columns_to_use]

    def fba_fees_txt_data(self, createdSince=None, createdUntil=None):
        report_type = "GET_FBA_ESTIMATED_FBA_FEES_TXT_DATA"
        if createdSince is None:
            createdSince = datetime.now() - timedelta(days=14)
        if createdUntil is None:
            createdUntil = datetime.now()
        print(f"Fetching FBA Fees Data Since: {createdSince} to {createdUntil}")
        report_ids = self._fetch_report_ids(
            "reportDocumentId",
            [report_type],
            100,
            createdSince=createdSince,
            createdUntil=createdUntil,
        )
        print(f"Reports To Fetch: {len(report_ids)}")
        data = self.fetch_reports(report_ids)
        return pd.DataFrame(data[1:], columns=data[0])

    def amz_settlement(self, createdSince=None, createdUntil=None, **kwargs):
        # pass createdSince or it will fetch last 14 days settlement report data.
        report_type = "GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE_V2"
        if createdSince is None:
            createdSince = datetime.now() - timedelta(days=14)
        kwargs["createdSince"] = createdSince
        if createdUntil is None:
            createdUntil = datetime.now()
        kwargs["createdUntil"] = createdUntil
        print(f"Fetching Settlement Reports Since: {createdSince} to {createdUntil}")
        report_ids = self._fetch_report_ids(
            "reportDocumentId", [report_type], 100, **kwargs
        )
        print(f"Reports To Fetch: {len(report_ids)}")
        data = self.fetch_reports(report_ids)
        return pd.DataFrame(data[1:], columns=data[0])

    def amz_returns(self, start_from: int, **kwargs):
        # Fetch last start_from days of customer returns data, update as needed
        report_type = "GET_FBA_FULFILLMENT_CUSTOMER_RETURNS_DATA"
        data = self.create_report(
            report_type, dataStartTime=datetime.now() - timedelta(days=start_from)
        )
        reportId = data.payload["reportId"]
        reportDocumentId = self.fetch_report_by_id(reportId)
        print(f"Report Document Id: {reportDocumentId}")
        data = self.fetch_reports([reportDocumentId])
        return pd.DataFrame(data[1:], columns=data[0])

    async def amz_sku_sale_price(self, skus: list):
        from kn_api._kn_sp_api.products import Products
        from django.core.paginator import Paginator

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

        paginator = Paginator(skus, 20)  # Create a Paginator object
        sku_lists = list()
        for page_number in paginator.page_range:
            page_skus = paginator.page(page_number)  # Get the skus for the current page
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
                MAX_RETRY = 10
                for _ in range(MAX_RETRY):  # MAX_RETRY times
                    print(
                        f"Retrying failed skus: Retry Count: {_+1} | Failed Count: {failed_count}"
                    )
                    failed_skus = get_failed_list(sku_results)
                    sku_results = await init_loop(sku_limiter, failed_skus)
                    success_retry = [i for i in sku_results if not isinstance(i, list)]
                    final_data.extend(success_retry)
                    failed_count = len(get_failed_list(sku_results))
                    if not failed_count:
                        break
                    time.sleep((failed_count / 0.5) + _)  # 0.5 Requests per second
                else:
                    list_fail = get_failed_list(sku_results)
                    total_fail = len(list_fail)
                    print(
                        f"Some skus failed after {MAX_RETRY} retries.\nFailed Count: {total_fail}\nSKU: {list_fail}"
                    )

            pass_count = 0
            for res in final_data:
                if not isinstance(res, list):
                    pass_count += 1
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

    async def amz_sku_product_type(self, sku_names):
        def filter_failed(get_results):
            return [i[0] for i in get_results if isinstance(i, list) and i[1] is None]

        from kn_api._kn_sp_api.listings_items import ListingsItems

        sellerId = "A1U16T1MFHGN7V"
        listing_client = ListingsItems(Marketplaces.IN)
        limiter_get = get_rate_limiter(10, 5)

        async def init_sku_get(sku_name):
            async with limiter_get:
                try:
                    with ThreadPoolExecutor() as executor:
                        loop = asyncio.get_event_loop()
                        data = await loop.run_in_executor(
                            executor,
                            lambda: listing_client.get_listings_item(
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
                [i for i in retry_results if isinstance(i, list) and i[1] is not None]
            )
            retry_get = filter_failed(retry_results)
        else:
            print(f"Some skus failed after 5 retries. {retry_get}")

        get_results = [
            i for i in get_results if isinstance(i, list) and i[1] is not None
        ]
        print(f"Pass: {len(get_results)} | Failed: {len(sku_names)-len(get_results)}")

        return pd.DataFrame(get_results, columns=["name", "product_type"])
