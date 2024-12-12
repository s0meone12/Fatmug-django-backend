from django.db import models
from ...sku import Sku
from ...inheritance import BaseModel
from core.manager.amz.sku.sku.main import AmzSkuManager
from django.core.exceptions import ValidationError


class AmzSku(BaseModel):
    manager = AmzSkuManager()
    int_sku = models.ForeignKey(
        Sku, on_delete=models.RESTRICT, blank=True, null=True)
    name = models.CharField(max_length=100, unique=True,
                            blank=False, null=False)
    asin = models.CharField(max_length=100, unique=True,
                            blank=False, null=False)
    product_type = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Product Type"
    )
    is_discontinued = models.BooleanField(
        default=False, blank=False, null=False)
    fba_inv_days = models.FloatField(blank=False, null=False, default=0.0)
    str_qc_re_rts_trns_fba_inv_days = models.FloatField(
        blank=False, null=False, default=0.0
    )
    desired_ads_percentage = models.FloatField(blank=False, null=False)

    sale_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, verbose_name="Current Sale Price"
    )
    unit_ads_spend = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, verbose_name="Unit Ads Spend"
    )
    mrp = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, verbose_name="MRP"
    )
    cost = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, verbose_name="Production Cost"
    )
    tax_rate = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, verbose_name="Tax Rate"
    )
    desired_profit = models.DecimalField(
        max_digits=5, decimal_places=2, null=False, verbose_name="Desire Profit"
    )
    recommended_sale_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        verbose_name="Recommended Sale Price",
    )
    round_recommended_sale_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        verbose_name="Round Recommended Sale Price",
    )
    to_publish_sale_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        verbose_name="To Publish Sale Price",
    )

    def __str__(self):
        return self.name

    def clean(self):
        # Constrains on recommended_sale_price
        if self.recommended_sale_price > self.mrp:
            raise ValidationError(
                {
                    "recommended_sale_price": "Discount price cannot be greater than the MRP."
                }
            )
        if self.recommended_sale_price < self.cost:
            raise ValidationError(
                {
                    "recommended_sale_price": "Discount price cannot be less than the production cost."
                }
            )
        # Constrains on desired_profit
        if self.desired_profit <= 0:
            raise ValidationError(
                {"desired_profit": "Desired profit margin should be greater than 0.0."}
            )
