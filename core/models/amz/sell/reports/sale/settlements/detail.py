from django.db import models
from ......inheritance import BaseModel
from .....sku import AmzSku
from .amount_description import AmzSettlementAmountDescription
from .amount_type import AmzSettlementAmountType
from .transaction_type import AmzSettlementTransactionType
from .main import AmzSettlement
from core.manager import AmzSettlementDetailManager


class AmzSettlementDetail(BaseModel):
    manager = AmzSettlementDetailManager()
    settlement = models.ForeignKey(
        AmzSettlement,
        on_delete=models.PROTECT,
        null=False,
        blank=False,
        verbose_name="Settlement",
        related_name="settlement_details",
    )
    transaction_type = models.ForeignKey(
        AmzSettlementTransactionType,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Transaction Type",
        related_name="transaction_types",
    )
    order_id = models.CharField(
        null=True, blank=True, max_length=50, verbose_name="Order ID"
    )
    merchant_order_id = models.CharField(
        null=True, blank=True, max_length=50, verbose_name="Merchant Order ID"
    )
    adjustment_id = models.CharField(
        null=True, blank=True, max_length=50, verbose_name="Adjustment ID"
    )
    shipment_id = models.CharField(
        null=True, blank=True, max_length=30, verbose_name="Shipment ID"
    )
    marketplace_name = models.CharField(
        null=True, blank=True, max_length=50, verbose_name="Marketplace Name"
    )
    amount_type = models.ForeignKey(
        AmzSettlementAmountType,
        on_delete=models.PROTECT,
        null=True,
        blank=False,
        verbose_name="Amount Type",
        related_name="amount_types",
    )
    amount_description = models.ForeignKey(
        AmzSettlementAmountDescription,
        on_delete=models.PROTECT,
        null=False,
        blank=False,
        verbose_name="Amount Description",
        related_name="amount_descriptions",
    )
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Amount")
    fulfillment_id = models.CharField(
        null=True, blank=True, max_length=30, verbose_name="Fulfillment ID"
    )
    posted_datetime = models.DateTimeField(verbose_name="Posted Date Time")
    order_item_code = models.CharField(
        null=True, blank=True, max_length=30, verbose_name="Order Item Code"
    )
    merchant_order_item_id = models.CharField(
        max_length=30, null=True, blank=True, verbose_name="Merchant Order Item ID"
    )
    merchant_adjustment_item_id = models.CharField(
        max_length=30, null=True, blank=True, verbose_name="Merchant Adjustment Item ID"
    )
    sku = models.ForeignKey(
        AmzSku,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="AMZ SKU",
        related_name="settlement_detail_skus",
    )
    quantity_purchased = models.IntegerField(
        null=True, blank=True, verbose_name="Quantity Purchased"
    )
    promotion_id = models.CharField(
        max_length=100, null=True, blank=True, verbose_name="Promotion ID"
    )

    class Meta:
        verbose_name = "Amazon Settlement Detail"
        verbose_name_plural = "Amazon Settlement Details"
        indexes = [
            models.Index(fields=["settlement"]),
            models.Index(fields=["order_id"]),
            models.Index(fields=["transaction_type"]),
            models.Index(fields=["amount_type"]),
            models.Index(fields=["amount_description"]),
            models.Index(fields=["posted_datetime"]),
            models.Index(fields=["sku"]),
        ]

    def __str__(self):
        return f"{self.settlement.settlement_id} - {self.transaction_type} - {self.amount_type} - {self.amount_description} - {self.amount}"
