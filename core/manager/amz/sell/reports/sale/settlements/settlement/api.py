from datetime import datetime, timedelta
import pandas as pd
from core.apis.clients import SP_FETCHER
from core.models.amz.sell.reports.sale.settlements import (
    AmzSettlementAmountDescription,
    AmzSettlementAmountType,
    AmzSettlement,
    AmzSettlementTransactionType,
)
from .main import AmzSettlementManager


class ApiSubManagerAmzSettlement:

    def __init__(self, manager: AmzSettlementManager):
        self.manager = manager
        self.__report = SP_FETCHER.AMZ_SPAPI_IN.reports.settlement

    def _transform_amz_settlement(self, df: pd.DataFrame) -> pd.DataFrame:
        pre_reserve_df = df[
            df["amount-description"] == "Previous Reserve Amount Balance"
        ]
        pre_reserve_df = pre_reserve_df[["settlement-id", "amount"]]

        cur_reserve_df = df[df["amount-description"]
                            == "Current Reserve Amount"]
        cur_reserve_df = cur_reserve_df[["settlement-id", "amount"]]

        df = df[df["total-amount"] != ""]
        columns_to_use = [
            "settlement-id",
            "settlement-start-date",
            "settlement-end-date",
            "deposit-date",
            "total-amount",
            "currency",
        ]
        df = df[columns_to_use]
        # For Data Frame Loaded from CSV / Replace NaN with ""
        df = df.fillna("")
        rename_col_data = {
            "settlement-id": "settlement_id",
            "settlement-start-date": "start_datetime",
            "settlement-end-date": "end_datetime",
            "deposit-date": "deposit_datetime",
            "total-amount": "total_amount",
            "amount_x": "previous_reserve_amount",
            "amount_y": "current_reserve_amount",
        }

        # Merge pre_reserve_df and cur_reserve_df with df using 'settlement-id'
        df = pd.merge(df, pre_reserve_df, how="left", on="settlement-id")
        df = pd.merge(df, cur_reserve_df, how="left", on="settlement-id")
        df.rename(columns=rename_col_data, inplace=True)

        # Convert the datetime format to the desired format
        df["start_datetime"] = pd.to_datetime(
            df["start_datetime"], format="%d.%m.%Y %H:%M:%S %Z"
        ).dt.strftime("%m.%d.%Y %H:%M:%S %Z")
        df["end_datetime"] = pd.to_datetime(
            df["end_datetime"], format="%d.%m.%Y %H:%M:%S %Z"
        ).dt.strftime("%m.%d.%Y %H:%M:%S %Z")
        df["deposit_datetime"] = pd.to_datetime(
            df["deposit_datetime"], format="%d.%m.%Y %H:%M:%S %Z"
        ).dt.strftime("%m.%d.%Y %H:%M:%S %Z")

        return df

    def _transform_amz_settlement_detail(self, df):

        columns_to_use = [
            "settlement-id",
            "transaction-type",
            "order-id",
            "merchant-order-id",
            "adjustment-id",
            "shipment-id",
            "marketplace-name",
            "amount-type",
            "amount-description",
            "amount",
            "fulfillment-id",
            "posted-date-time",
            "order-item-code",
            "merchant-order-item-id",
            "merchant-adjustment-item-id",
            "sku",
            "quantity-purchased",
            "promotion-id",
        ]
        df = df[columns_to_use]
        rename_column_data = {
            "settlement-id": "settlement",
            "transaction-type": "transaction_type",
            "order-id": "order_id",
            "merchant-order-id": "merchant_order_id",
            "adjustment-id": "adjustment_id",
            "shipment-id": "shipment_id",
            "marketplace-name": "marketplace_name",
            "amount-type": "amount_type",
            "amount-description": "amount_description",
            "amount": "amount",
            "fulfillment-id": "fulfillment_id",
            "posted-date-time": "posted_datetime",
            "order-item-code": "order_item_code",
            "merchant-order-item-id": "merchant_order_item_id",
            "merchant-adjustment-item-id": "merchant_adjustment_item_id",
            "sku": "sku",
            "quantity-purchased": "quantity_purchased",
            "promotion-id": "promotion_id",
        }
        df.rename(columns=rename_column_data, inplace=True)
        # For Data Frame Loaded from CSV / Replace NaN with ""
        df = df.fillna("")

        # Get AmzSettlement Unique id And Make A Map
        unique_settlement_id = df["settlement"].unique()
        s_id_map = {
            settlement.settlement_id: settlement
            for settlement in AmzSettlement.objects.filter(
                settlement_id__in=unique_settlement_id
            )
        }
        for sid in s_id_map.values():
            if sid.settlement_details.filter().first():
                # If Data Already Present Skip This Settlement ID
                print(f"{sid} Data Already Exist")
                df = df[df["settlement"] != sid.settlement_id]

        # Get Or Create AmzSettlementTransactionType And Make A Map
        unique_transaction_type = {
            at for at in df["transaction_type"].unique() if at}
        AmzSettlementTransactionType.get_or_create_by_name_values(
            unique_transaction_type
        )

        # Get Or Create AmzSettlementAmountDescription And Make A Map
        unique_amount_description = {
            ad for ad in df["amount_description"].unique() if ad
        }
        AmzSettlementAmountDescription.get_or_create_by_name_values(
            unique_amount_description
        )

        # Get Or Create AmzSettlementAmountType And Make A Map
        unique_amount_type = {at for at in df["amount_type"].unique() if at}
        AmzSettlementAmountType.get_or_create_by_name_values(
            unique_amount_type)

        df["settlement"] = df["settlement"].apply(
            lambda name: {"settlement_id": name})
        df["sku"] = df["sku"].apply(
            lambda name: {"name": name} if name else "")
        df["transaction_type"] = df["transaction_type"].apply(
            lambda name: {"name": name} if name else ""
        )
        df["amount_description"] = df["amount_description"].apply(
            lambda name: {"name": name} if name else ""
        )
        df["amount_type"] = df["amount_type"].apply(
            lambda name: {"name": name} if name else ""
        )

        # Convert the datetime to the desired format
        df["posted_datetime"] = pd.to_datetime(
            df["posted_datetime"], format="%d.%m.%Y %H:%M:%S %Z"
        )
        df["posted_datetime"] = df["posted_datetime"].dt.strftime(
            "%m.%d.%Y %H:%M:%S %Z"
        )

        # Remove 'Current Reserve Amount', 'Previous Reserve Amount Balance' as its already present in AmzSettlement
        df = df[
            ~df["amount_description"].isin(
                ["Current Reserve Amount", "Previous Reserve Amount Balance"]
            )
        ]

        # Drop where posted_datetime is blank
        df = df.dropna(subset=["posted_datetime"])

        # Make Quantity Purchased default to 0 where it's blank or nan
        df["quantity_purchased"].fillna(0, inplace=True)
        df["quantity_purchased"] = df["quantity_purchased"].replace("", 0)
        df["quantity_purchased"] = df["quantity_purchased"].astype("int64")
        df["id"] = None

        return df

    def _read(
        self, from_days_ago: int | None = None, to_days_until: int | None = None
    ) -> pd.DataFrame:
        createdSince = (
            datetime.now() - timedelta(days=from_days_ago) if from_days_ago else None
        )
        createdUntil = (
            datetime.now() + timedelta(days=to_days_until) if to_days_until else None
        )
        df = self.__report.get_report(
            createdSince=createdSince, createdUntil=createdUntil
        )
        return df

    # Should have had option to pass days, with hints on the range allowed. And the default should be max days possible.
    def sync(
        self, from_days_ago: int | None = None, to_days_until: int | None = None
    ) -> pd.DataFrame:
        """
        Days range cannot be more than 90 days.
        """
        from core.models.amz.sell.reports.sale.settlements import AmzSettlementDetail

        df = self._read(from_days_ago, to_days_until)
        print('df.shape[0]: ', df.shape[0])
        amz_settlement_df = self._transform_amz_settlement(df.copy())
        self.manager.dfdb.sync(df=amz_settlement_df)
        amz_settlement_detail_df = self._transform_amz_settlement_detail(df)
        AmzSettlementDetail.manager.dfdb.sync(
            df=amz_settlement_detail_df)
        return df
