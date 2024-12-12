from django.db import models
from ...inheritance import BaseModel
from ..sell.reports.sale.settlements import AmzSettlementAmountType, AmzSettlementAmountDescription
from .main import AmzSku
from core.manager import AmzSkuSettlementManager


class AmzSkuSettlement(BaseModel):
    manager = AmzSkuSettlementManager()
    sku = models.ForeignKey(
        AmzSku,
        on_delete=models.PROTECT,
        null=False,
        blank=False,
        verbose_name="SKU",
        related_name="settlement_skus",
    )
    amount_type = models.ForeignKey(
        AmzSettlementAmountType,
        on_delete=models.PROTECT,
        null=False,
        blank=False,
        verbose_name="Amount Type",
    )
    amount_description = models.ForeignKey(
        AmzSettlementAmountDescription,
        on_delete=models.PROTECT,
        null=False,
        blank=False,
        verbose_name="Amount Description",
    )
    avg_amount_value = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, verbose_name="Average Amount Value"
    )

    def __str__(self):
        return self.sku.name

    class Meta:
        verbose_name = "Amazon Settlement SKU"
        verbose_name_plural = "Amazon Settlement SKUs"
        unique_together = (
            "sku",
            "amount_description",
        )
        indexes = [
            models.Index(fields=["sku"]),
            models.Index(fields=["amount_type"]),
            models.Index(fields=["amount_description"]),
        ]
