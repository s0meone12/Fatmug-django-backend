from django.db import models
from .....inheritance import BaseModel
from ....sku import AmzSku
from core.manager import SkuPriceActionManager


class SkuPriceAction(BaseModel):
    manager = SkuPriceActionManager()
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")
    sale_start_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Sale Start Date"
    )
    sale_end_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Sale End Date"
    )
    sku = models.ForeignKey(
        AmzSku,
        on_delete=models.PROTECT,
        null=False,
        blank=False,
        verbose_name="AMZ SKU",
    )
    old_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=False,
        blank=False,
        editable=False,
        verbose_name="Old Price With Tax",
    )
    our_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=False,
        blank=False,
        editable=False,
        verbose_name="Standard Price With Tax",
    )
    discounted_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=False,
        blank=False,
        verbose_name="Discounted Price With Tax",
    )
    STATUS_CHOICES = [
        ("draft", "draft"),
        ("accepted", "accepted"),
        ("invalid", "invalid"),
        ("error", "error"),
    ]
    status = models.CharField(
        max_length=25,
        blank=False,
        null=False,
        choices=STATUS_CHOICES,
        default="draft",
        verbose_name="Current Status",
    )
    submission_id = models.CharField(
        max_length=50, null=True, blank=True, verbose_name="Submission ID"
    )
    issues = models.TextField(null=True, blank=True,
                              default="", verbose_name="Issues")

    def __str__(self):
        return f"{self.sku}"

    class Meta:
        verbose_name = "Amazon SKU Price Action"
        verbose_name_plural = "Amazon SKU Price Actions"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["sku"]),
                   models.Index(fields=["sku", "status"])]
