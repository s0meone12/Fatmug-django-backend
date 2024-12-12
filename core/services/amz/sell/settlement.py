from core.services.amz.sell import AmzSellService
from core.models.amz.sell.reports.sale.settlements import (
    AmzSettlementDetail,
    AmzSkuSettlement,
    AmzSettlementAmountDescription,
    AmzSettlementTransactionType,
)

from decimal import Decimal
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def _get_transaction_type(names: list):
    if len(names) == 1:
        for name in names:
            return AmzSettlementTransactionType.objects.get(name=name)
    return {AmzSettlementTransactionType.objects.get(name=name) for name in names}


def _cal_sku_avg_amount(df: pd.DataFrame):
    transaction_type_refund = _get_transaction_type(["Refund"])
    transaction_type_order = _get_transaction_type(["Order"])
    principal = AmzSettlementAmountDescription.objects.get(name="Principal")
    # Aggregate 'amount' and 'quantity_purchased' for common 'sku_id', 'amount_type_id', 'amount_description_id'
    aggregated_df = (
        df.groupby(
            ["sku_id", "transaction_type_id",
                "amount_type_id", "amount_description_id"]
        )
        .agg(
            total_amount=("amount", "sum"),
            total_quantity_purchased=("quantity_purchased", "sum"),
        )
        .reset_index()
    )
    aggregated_df["total_quantity_purchased"] = aggregated_df[
        "total_quantity_purchased"
    ].replace(0, np.nan)
    aggregated_df["per_unit_price"] = aggregated_df["total_amount"] / aggregated_df[
        "total_quantity_purchased"
    ].apply(Decimal)

    def calculate_final_quantity(row, order_data):
        # Only calculate for NaN values and transaction_type_id for 'Refund'
        if (
            pd.isna(row["total_quantity_purchased"])
            and row["transaction_type_id"] == transaction_type_refund.id
        ):
            matching_order = order_data[
                (order_data["sku_id"] == row["sku_id"])
                & (order_data["amount_type_id"] == row["amount_type_id"])
                & (order_data["amount_description_id"] == row["amount_description_id"])
            ]
            if not matching_order.empty:
                per_unit_price = matching_order["per_unit_price"].values[0]
                if per_unit_price != 0:
                    return round(row["total_amount"] / per_unit_price)
        return row["total_quantity_purchased"]

    # Filter 'aggregated_df' for 'Order' transaction_type_id rows to use as reference
    order_data = aggregated_df[
        aggregated_df["transaction_type_id"] == transaction_type_order.id
    ]

    # Apply the calculation across the DataFrame
    aggregated_df["final_quantity"] = aggregated_df.apply(
        calculate_final_quantity, order_data=order_data, axis=1
    )

    # Replace 'total_quantity_purchased' with 'final_quantity' where appropriate
    aggregated_df["total_quantity_purchased"].update(
        aggregated_df["final_quantity"])

    # Optional: Clean up, drop 'final_quantity' and 'per_unit_price'
    aggregated_df.drop(
        columns=["final_quantity", "per_unit_price"], inplace=True)

    # Now Find Unique amount_description from both transaction_type, substract the qty as per final_qty_data
    # Step 1: Group by the specified identifiers and count distinct transaction_type_id
    grouped = aggregated_df.groupby(
        ["sku_id", "amount_type_id", "amount_description_id"]
    )

    # Step 2: Identify groups where transaction_type_id count > 1
    groups_to_remove = grouped.filter(
        lambda x: x["transaction_type_id"].nunique() > 1)
    # If groups_to_remove is empty, there's nothing more to do
    if groups_to_remove.empty:
        print("No records match the criteria for removal.")
        cleaned_df = pd.DataFrame()
    else:
        # Step 3: Filter out these groups from the original DataFrame
        # This can be done by merging the groups to remove with the original DataFrame and then filtering
        merged = aggregated_df.merge(
            groups_to_remove.drop_duplicates(),
            on=["sku_id", "amount_type_id", "amount_description_id"],
            how="left",
            indicator=True,
        )
        cleaned_df = merged[merged["_merge"] ==
                            "left_only"].drop(columns="_merge")
        cleaned_df.rename(
            columns={
                "transaction_type_id_x": "transaction_type_id",
                "total_amount_x": "amount",
                "total_quantity_purchased_x": "quantity_purchased",
            },
            inplace=True,
        )
        cleaned_df.drop(
            columns=[
                "transaction_type_id_y",
                "total_amount_y",
                "total_quantity_purchased_y",
            ],
            inplace=True,
        )

    aggregated_df = (
        aggregated_df.groupby(
            ["sku_id", "amount_type_id", "amount_description_id"])
        .agg(
            transaction_type_id=(
                "transaction_type_id",
                lambda x: (
                    transaction_type_order.id
                    if transaction_type_order.id in x.values
                    else transaction_type_refund.id
                ),
            ),
            amount=("total_amount", "sum"),
            quantity_purchased=("total_quantity_purchased", "sum"),
        )
        .reset_index()
    )

    if not cleaned_df.empty:
        # Update unique amount_description qty
        principal_records = aggregated_df[
            (aggregated_df["amount_description_id"] == principal.id)
            & (aggregated_df["transaction_type_id"] == transaction_type_order.id)
        ][["sku_id", "quantity_purchased"]]

        cleaned_df = pd.merge(
            cleaned_df,
            principal_records,
            on="sku_id",
            how="left",
            suffixes=("", "_principal"),
        )

        cleaned_df["quantity_purchased"] = np.where(
            pd.notna(cleaned_df["quantity_purchased_principal"]),
            cleaned_df["quantity_purchased_principal"],
            cleaned_df["quantity_purchased"],
        )
        cleaned_df.drop(columns=["quantity_purchased_principal"], inplace=True)

        # Step 1: Merge aggregated_df with cleaned_df based on the matching criteria
        # Note: Ensure both DataFrames have the necessary columns for a match.
        merged_df = pd.merge(
            aggregated_df,
            cleaned_df[
                [
                    "sku_id",
                    "amount_type_id",
                    "amount_description_id",
                    "transaction_type_id",
                    "quantity_purchased",
                ]
            ],
            on=[
                "sku_id",
                "amount_type_id",
                "amount_description_id",
                "transaction_type_id",
            ],
            how="left",
            suffixes=("", "_cleaned"),
        )

        # Step 2: Conditionally update 'quantity_purchased' in aggregated_df based on the match
        merged_df["quantity_purchased"] = np.where(
            pd.notna(merged_df["quantity_purchased_cleaned"]),
            merged_df["quantity_purchased_cleaned"],
            merged_df["quantity_purchased"],
        )

        # Drop the '_cleaned' column after the update
        merged_df.drop(columns=["quantity_purchased_cleaned"], inplace=True)

        # Replace aggregated_df with the updated merged_df if needed
        aggregated_df = merged_df

    # Ensure 'quantity_purchased' stays as int and handle NaN values
    aggregated_df["quantity_purchased"] = (
        aggregated_df["quantity_purchased"].fillna(0).astype(int)
    )

    # Handle the situation where there is no quantity_purchased due to absence of Order data in DB
    aggregated_df = aggregated_df[aggregated_df["quantity_purchased"] != 0]

    # Calculate Average Amount:
    aggregated_df["avg_amount_value"] = (
        aggregated_df["amount"] / aggregated_df["quantity_purchased"]
    )

    # Clean the DF
    aggregated_df.drop(columns=["amount", "quantity_purchased"], inplace=True)
    aggregated_df.rename(
        columns={
            "sku_id": "sku",
            "transaction_type_id": "transaction_type",
            "amount_type_id": "amount_type",
            "amount_description_id": "amount_description",
        },
        inplace=True,
    )

    return aggregated_df


def _filter_settlement_by_days(
    past_days: int, transaction_type: list, values: list
) -> pd.DataFrame:
    from_date = datetime.now() - timedelta(days=past_days)
    transaction_type = _get_transaction_type(transaction_type)

    # Fetch the queryset for order_id in order_ids
    details_qs = AmzSettlementDetail.objects.filter(
        transaction_type__in=(
            transaction_type
            if isinstance(transaction_type, set)
            else {transaction_type}
        ),
        posted_datetime__gte=from_date,
    ).values(*values)

    # Convert QuerySet to a list of dictionaries
    details_list = list(details_qs)

    # Load into a Pandas DataFrame
    df = pd.DataFrame(details_list)
    if df.empty:
        print(f"No data found for settlement by days")
        return pd.DataFrame()
    return df


def _filter_settlement_by_count(
    count: int, transaction_type: list, exclude_sku_ids: set, values: list
) -> pd.DataFrame:
    transaction_type = _get_transaction_type(transaction_type)
    details_qs = (
        AmzSettlementDetail.objects.exclude(sku_id__in=exclude_sku_ids)
        .filter(
            transaction_type__in=(
                transaction_type
                if isinstance(transaction_type, set)
                else {transaction_type}
            ),
        )
        .order_by("-posted_datetime")
        .values(*values)
    )
    # Convert QuerySet to a list of dictionaries
    details_list = list(details_qs)

    # Load into a Pandas DataFrame
    df = pd.DataFrame(details_list)
    # Define an empty DataFrame to store the final result
    final_df = pd.DataFrame()
    # Iterate over each SKU group
    for sku, group in df.groupby("sku_id"):
        # Identify the first count unique order_ids
        unique_order_ids = group["order_id"].drop_duplicates().head(count)

        # Filter the original group to keep only records with these order_ids
        filtered_group = group[group["order_id"].isin(unique_order_ids)]

        # Concatenate the filtered group to the final DataFrame
        final_df = pd.concat([final_df, filtered_group])

    final_df.reset_index(drop=True, inplace=True)
    if final_df.empty:
        print(f"No data found for settlement by count")
        return pd.DataFrame()
    return final_df


class AmzSettlementService:
    def __init__(self):
        self.past_days = 90
        self.count = 1000

    def aggregate_data(self, **kwargs):
        sales_service = AmzSellService()
        sales_service.aggregate_settlement_data(**kwargs)

    def cal_sku_avg(self) -> None:
        df_by_days = self._cal_sku_avg_amount_by_days()
        exclude_sku_ids = set()
        if not df_by_days.empty:
            exclude_sku_ids = set(df_by_days["sku"].unique())
        else:
            df_by_days = pd.DataFrame(
                [
                    "sku",
                    "amount_type",
                    "amount_description",
                    "transaction_type",
                    "avg_amount_value",
                ]
            )
        df_by_count = self._cal_sku_avg_amount_by_count(exclude_sku_ids)
        print(f"exclude_sku_ids: {exclude_sku_ids}")
        if df_by_count.empty:
            df_by_count = pd.DataFrame(
                [
                    "sku",
                    "amount_type",
                    "amount_description",
                    "transaction_type",
                    "avg_amount_value",
                ]
            )
        if df_by_days.size > 5 and df_by_count.size > 5:
            print("Data by days and count found for sku avg")
            df = pd.concat([df_by_days, df_by_count])
        elif df_by_days.size > 5:
            print("Only data found for sku avg by days")
            df = df_by_days
        elif df_by_count.size > 5:
            print("Only data found for sku avg by count")
            df = df_by_count
        else:
            print("No data found for sku avg")
            df = pd.DataFrame()
        print(df)
        if not df.empty:
            AmzSkuSettlement.dfdb.sync(df=df)

    def _cal_sku_avg_amount_by_days(self) -> pd.DataFrame:
        df = _filter_settlement_by_days(
            self.past_days,
            ["Order", "Refund"],
            [
                "sku_id",
                "transaction_type_id",
                "amount_type_id",
                "amount_description_id",
                "amount",
                "quantity_purchased",
            ],
        )
        if not df.empty:
            df_by_days = _cal_sku_avg_amount(df)
        else:
            df_by_days = df
        return df_by_days

    def _cal_sku_avg_amount_by_count(self, exclude_sku_ids: set) -> pd.DataFrame:
        df = _filter_settlement_by_count(
            self.count,
            ["Order", "Refund"],
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
            df_by_count = _cal_sku_avg_amount(df)
        else:
            df_by_count = df
        return df_by_count
