import pandas as pd
from core.apis.clients import SP_FETCHER
from core.models import (
    AmzSaleReturnDetailedDisposition,
    AmzSaleReturnReason,
)
from .main import AmzSaleReturnManager


class ApiSubManagerAmzSaleReturn:

    def __init__(self, manager: AmzSaleReturnManager):
        self.manager = manager
        self.__report = SP_FETCHER.AMZ_SPAPI_IN.reports.sale_return

    def _transform_df(self, df: pd.DataFrame) -> pd.DataFrame:

        columns_to_use = [
            "return-date",
            "order-id",
            "sku",
            "quantity",
            "fulfillment-center-id",
            "detailed-disposition",
            "reason",
            "license-plate-number",
            "customer-comments",
        ]
        df = df[columns_to_use]
        df.rename(
            columns={
                "return-date": "return_datetime",
                "order-id": "order_id",
                "quantity": "quantity",
                "fulfillment-center-id": "fulfillment_center_id",
                "detailed-disposition": "detailed_disposition",
                "license-plate-number": "license_plate_number",
                "customer-comments": "customer_comments",
            },
            inplace=True,
        )
        # For Data Frame Loaded from CSV / Replace NaN with ""
        df = df.fillna("")
        # Get Or Create AmzSaleReturnDetailedDisposition And Make A Map
        unique_detailed_disposition_type = {
            dd for dd in df["detailed_disposition"].unique() if dd
        }
        # Model.manager.get_or_create_by_name_values(unique_detailed_disposition_type)
        AmzSaleReturnDetailedDisposition.get_or_create_by_name_values(
            unique_detailed_disposition_type
        )

        # Get Or Create AmzSaleReturnReason And Make A Map
        unique_reason_type = {r for r in df["reason"].unique() if r}
        AmzSaleReturnReason.get_or_create_by_name_values(unique_reason_type)

        df["sku"] = df["sku"].apply(
            lambda name: {"name": name} if name else "")
        df["detailed_disposition"] = df["detailed_disposition"].apply(
            lambda name: {"name": name} if name else ""
        )
        df["reason"] = df["reason"].apply(
            lambda name: {"name": name} if name else "")

        # Convert 'return_datetime' to the desired format
        df["return_datetime"] = pd.to_datetime(df["return_datetime"], utc=True)
        df["return_datetime"] = (
            df["return_datetime"]
            .dt.tz_convert("UTC")
            .dt.strftime("%m.%d.%Y %H:%M:%S %Z")
        )

        return df

    def _read(self, from_days_ago: int | None = None) -> pd.DataFrame:
        df = self.__report.get_report(from_days_ago)
        df = self._transform_df(df)
        return df

    def sync(self, from_days_ago: int | None = None) -> pd.DataFrame:
        df = self._read(from_days_ago)
        self.manager.dfdb.sync(df=df)
        return df
