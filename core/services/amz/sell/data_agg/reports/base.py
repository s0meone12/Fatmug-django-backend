# from h11 import Data
import pandas as pd
from core.models.amz.sell.reports.sale.settlements import (
    AmzSettlementAmountDescription,
    AmzSettlementAmountType,
    AmzSettlement,
    AmzSettlementTransactionType,
)
from core.models.amz.sell.reports.sale.returns import (
    AmzSaleReturnDetailedDisposition,
    AmzSaleReturnReason,
)


class AmzSellReportsBaseDataAggregationService:
    def __init__(self):
        pass

    def _transform_sell_order_rpt_columns(self, df):
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
        df = df[df['sku'] != 'UNKNOW']

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

    def _transform_amz_settlement_rpt_columns(self, df):
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

    def _transform_amz_settlement_detail_rpt_columns(self, df):
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

    def _transform_amz_return_rpt_columns(self, df: pd.DataFrame):
        print("Got DF2")
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
