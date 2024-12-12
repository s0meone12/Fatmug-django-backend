from django.db import models
from ......inheritance import BaseModel
from core.models.amz.sku.main import AmzSku
from core.manager.amz.sell.reports.sale.returns import AmzSaleReturnManager
from .disposition import AmzSaleReturnDetailedDisposition
from .reason import AmzSaleReturnReason


class AmzSaleReturn(BaseModel):
    manager = AmzSaleReturnManager()
    sku = models.ForeignKey(
        AmzSku,
        on_delete=models.PROTECT,
        null=False,
        blank=False,
        verbose_name="AMZ SKU",
        related_name="return_skus",
    )
    return_datetime = models.DateTimeField(verbose_name="Return Datetime")
    order_id = models.CharField(
        null=False, blank=False, max_length=50, verbose_name="Order ID"
    )
    quantity = models.PositiveIntegerField(
        null=False, blank=False, verbose_name="Quantity Return"
    )
    fulfillment_center_id = models.CharField(
        null=False, blank=False, max_length=8, verbose_name="Fulfillment Center ID"
    )
    detailed_disposition = models.ForeignKey(
        AmzSaleReturnDetailedDisposition,
        on_delete=models.PROTECT,
        null=False,
        blank=False,
        verbose_name="Detailed Disposition",
        related_name="detailed_dispositions",
    )
    reason = models.ForeignKey(
        AmzSaleReturnReason,
        on_delete=models.PROTECT,
        null=False,
        blank=False,
        verbose_name="Reason",
        related_name="reasons",
    )
    license_plate_number = models.CharField(
        null=False, blank=False, max_length=30, verbose_name="License Plate Number"
    )
    customer_comments = models.TextField(
        null=True, blank=True, verbose_name="Customer Comment"
    )

    def __str__(self):
        return f"{self.sku} - {self.return_datetime}"

    class Meta:
        verbose_name = "Amazon Return"
        verbose_name_plural = "Amazon Returns"
        unique_together = (
            "sku",
            "order_id",
            "fulfillment_center_id",
            "license_plate_number",
        )
        indexes = [
            models.Index(fields=["sku"]),
            models.Index(fields=["return_datetime"]),
            models.Index(fields=["order_id"]),
            models.Index(fields=["detailed_disposition"]),
            models.Index(fields=["reason"]),
        ]
