from django.db import models
from core.models.inheritance import BaseModel
from core.manager import AmzSettlementManager


class AmzSettlement(BaseModel):
    manager = AmzSettlementManager()
    settlement_id = models.CharField(
        max_length=30, unique=True, verbose_name="Settlement ID"
    )

    start_datetime = models.DateTimeField(verbose_name="Start Datetime")
    end_datetime = models.DateTimeField(verbose_name="End Datetime")
    deposit_datetime = models.DateTimeField(
        null=True, blank=True, verbose_name="Deposit Datetime"
    )

    total_amount = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Total Amount"
    )
    currency = models.CharField(max_length=6, verbose_name="Currency")
    previous_reserve_amount = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Previous Reserve Amount"
    )
    current_reserve_amount = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Current Reserve Amount"
    )

    def __str__(self):
        return self.settlement_id

    class Meta:
        verbose_name = "Amazon Settlement"
        verbose_name_plural = "Amazon Settlements"
        indexes = [
            models.Index(fields=["settlement_id"]),
            models.Index(fields=["start_datetime"]),
            models.Index(fields=["end_datetime"]),
        ]
