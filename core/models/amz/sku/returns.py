from django.db import models
from core.models.inheritance import BaseModel
from .main import AmzSku
from ..sell.reports.sale.returns.disposition import AmzSaleReturnDetailedDisposition
from core.manager import AmzSkuSaleReturnManager


class AmzSkuSaleReturn(BaseModel):
    sku = models.ForeignKey(
        AmzSku, on_delete=models.PROTECT, null=False, blank=False, verbose_name="SKU"
    )
    detailed_disposition = models.ForeignKey(
        AmzSaleReturnDetailedDisposition,
        on_delete=models.PROTECT,
        null=False,
        blank=False,
        verbose_name="Detailed Disposition",
    )
    total_return_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Percentage of return out of all return types",
    )
    total_order_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Percentage of return out of all orders",
    )
    manager = AmzSkuSaleReturnManager()

    def __str__(self):
        return f"{self.sku}"

    class Meta:
        verbose_name = "Amazon Return Sku"
        verbose_name_plural = "Amazon Return Skus"
        unique_together = ("sku", "detailed_disposition")

        indexes = [
            models.Index(fields=["sku"]),
            models.Index(fields=["sku", "detailed_disposition"]),
        ]
