import pandas as pd
from core.apis.clients import SP_FETCHER
from .main import SaleOrderRptManager


class AmzApiSubManagerSaleOrderRpt:

    def __init__(self, manager: SaleOrderRptManager):
        self.manager = manager
        self.__report = SP_FETCHER.AMZ_SPAPI_IN.reports.sale_order

    def _transform_df(self, df: pd.DataFrame) -> pd.DataFrame:
        columns_to_use = [
            "amazon-order-id",
            "purchase-date",
            "item-status",
            "sku",
            "quantity",
            "item-price",
            "ship-city",
            "ship-state",
            "ship-postal-code",
        ]
        df = df[columns_to_use]
        # Exclude rows where sku is "UNKNOW"
        df = df[df["sku"] != "UNKNOW"]

        rename_col_data = {
            "amazon-order-id": "amazon_order_id_code",
            "purchase-date": "purchase_date",
            "item-status": "order_status",
            "sku": "sku",
            "quantity": "quantity",
            "item-price": "item_price",
            "ship-city": "ship_city",
            "ship-state": "ship_state",
            "ship-postal-code": "ship_postal_code",
        }
        df.rename(columns=rename_col_data, inplace=True)
        df = df.drop_duplicates(subset=["amazon_order_id_code", "sku"])
        df["sku"] = df["sku"].apply(lambda x: {"name": x})
        df["item_price"].fillna(0, inplace=True)
        df["item_price"] = df["item_price"].replace("", 0.0)
        return df

    def _read(
        self, from_days_ago: int | None = None, to_days_until: int | None = None
    ) -> pd.DataFrame:
        return self._transform_df(
            self.__report.get_report(from_days_ago, to_days_until)
        )

    def sync(
        self, from_days_ago: int | None = None, to_days_until: int | None = None
    ) -> pd.DataFrame:
        df = self._read(from_days_ago, to_days_until)
        self.manager.dfdb.sync(df=df, fk_strict=False)
        return df
