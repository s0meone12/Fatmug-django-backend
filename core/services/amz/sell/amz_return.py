from core.models.amz.sell.reports.sale.settlements import AmzSettlementTransactionType
from core.services.amz.sell import AmzSellService
from core.models.amz.sell.reports.sale.returns import AmzSaleReturn
import pandas as pd
from core.services.amz.sell.settlement import (
    _filter_settlement_by_days,
    _filter_settlement_by_count,
)
from core.models.amz.sell.reports.sale.returns import AmzSaleReturnSku


def fetch_refund_by_order_id(order_id: set, values: list):
    details_qs = AmzSaleReturn.objects.filter(
        order_id__in=order_id).values(*values)
    # Convert QuerySet to a list of dictionaries
    details_list = list(details_qs)

    # Load into a Pandas DataFrame
    df = pd.DataFrame(details_list)
    return df


def cal_sku_avg_amount(df: pd.DataFrame):
    if df.empty:
        # Define the column names
        columns = [
            "sku_id",
            "detailed_disposition_id",
            "total_return_percentage",
            "total_order_percentage",
        ]
        # Create an empty DataFrame with the specified columns
        empty_df = pd.DataFrame(columns=columns)
        return empty_df
    transaction_type_order = AmzSettlementTransactionType.objects.get(
        name="Order")
    refund_order_id = df[df["transaction_type_id"] == transaction_type_order.id][
        "order_id"
    ].unique()
    rdf = fetch_refund_by_order_id(
        refund_order_id,
        ["sku_id", "order_id", "detailed_disposition_id", "reason_id", "quantity"],
    )
    RDF = (
        rdf.groupby(["sku_id"]).agg(
            total_qty_return=("quantity", "sum")).reset_index()
    )
    ODF = (
        df.groupby(["sku_id"])
        .agg(total_qty_order=("quantity_purchased", "sum"))
        .reset_index()
    )
    DF = pd.merge(
        ODF[["sku_id", "total_qty_order"]],
        RDF[["sku_id", "total_qty_return"]],
        on=["sku_id"],
        how="inner",
    )

    return_percentage = (
        rdf.groupby(["sku_id", "detailed_disposition_id"])
        .agg(total_quantity=("quantity", "sum"))
        .reset_index()
    )
    # Merge the two DataFrames on 'sku_id'
    merged_df_total_order = pd.merge(
        return_percentage, DF[["sku_id", "total_qty_order"]], on="sku_id"
    )

    # Calculate the return percentage
    merged_df_total_order["total_order_percentage"] = (
        merged_df_total_order["total_quantity"]
        / merged_df_total_order["total_qty_order"]
    ) * 100
    merged_df_total_order.drop(
        columns=["total_quantity", "total_qty_order"], inplace=True
    )

    return_percentage = (
        rdf.groupby(["sku_id", "detailed_disposition_id"])
        .agg(total_quantity=("quantity", "sum"))
        .reset_index()
    )
    # Merge the two DataFrames on 'sku_id'
    merged_df_total_return = pd.merge(
        return_percentage, DF[["sku_id", "total_qty_return"]], on="sku_id"
    )

    # Calculate the return percentage
    merged_df_total_return["total_return_percentage"] = (
        merged_df_total_return["total_quantity"]
        / merged_df_total_return["total_qty_return"]
    ) * 100
    merged_df_total_return.drop(
        columns=["total_quantity", "total_qty_return"], inplace=True
    )

    merged_df = pd.merge(
        merged_df_total_return,
        merged_df_total_order[
            ["sku_id", "detailed_disposition_id", "total_order_percentage"]
        ],
        on=["sku_id", "detailed_disposition_id"],
    )

    merged_df.rename(
        columns={
            "sku_id": "sku",
            "detailed_disposition_id": "detailed_disposition",
        },
        inplace=True,
    )

    return merged_df


class AmzSaleReturnService:

    def __init__(self):
        self.num_of_reports = 100
        self.past_days = 90
        self.count = 1000

    def aggregate_data(self, **kwargs):
        sales_service = AmzSellService()
        sales_service.aggregate_return_data(**kwargs)

    def cal_sku_avg(self):
        df_by_days = self.cal_sku_avg_amount_by_days()
        exclude_sku_ids = set()
        if not df_by_days.empty:
            exclude_sku_ids = df_by_days["sku"].unique()
        else:
            df_by_days = pd.DataFrame(
                [
                    "sku",
                    "detailed_disposition",
                    "total_return_percentage",
                    "total_order_percentage",
                ]
            )
        df_by_count = self.cal_sku_avg_amount_by_count(exclude_sku_ids)
        print(f"exclude_sku_ids: {exclude_sku_ids}")
        if df_by_count.empty:
            df_by_count = pd.DataFrame(
                [
                    "sku",
                    "detailed_disposition",
                    "total_return_percentage",
                    "total_order_percentage",
                ]
            )

        if df_by_days.size > 4 and df_by_count.size > 4:
            print("Data by days and count found for sku avg")
            df = pd.concat([df_by_days, df_by_count])
        elif df_by_days.size > 4:
            print("Only data found for sku avg by days")
            df = df_by_days
        elif df_by_count.size > 4:
            print("Only data found for sku avg by count")
            df = df_by_count
        else:
            print("No data found for sku avg")
            df = pd.DataFrame()
        print(df)
        if not df.empty:
            AmzSaleReturnSku.dfdb.sync(df=df)

    def cal_sku_avg_amount_by_days(self) -> pd.DataFrame:
        df = _filter_settlement_by_days(
            self.past_days,
            ["Order"],
            [
                "sku_id",
                "order_id",
                "transaction_type_id",
                "amount_type_id",
                "amount_description_id",
                "amount",
                "quantity_purchased",
            ],
        )

        if not df.empty:
            df_by_days = cal_sku_avg_amount(df)
        else:
            df_by_days = df
        return df_by_days

    def cal_sku_avg_amount_by_count(self, exclude_sku_ids: set) -> pd.DataFrame:
        df = _filter_settlement_by_count(
            self.count,
            ["Order"],
            exclude_sku_ids,
            [
                "sku_id",
                "order_id",
                "transaction_type_id",
                "amount_type_id",
                "amount_description_id",
                "amount",
                "quantity_purchased",
            ],
        )

        if not df.empty:
            df_by_count = cal_sku_avg_amount(df)
        else:
            df_by_count = pd.DataFrame(
                [
                    "sku",
                    "detailed_disposition",
                    "total_return_percentage",
                    "total_order_percentage",
                ]
            )
        return df_by_count
