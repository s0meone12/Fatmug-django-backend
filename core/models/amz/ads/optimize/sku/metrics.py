from django.db import models
from ....sku.main import AmzSku
from .....inheritance.base_model import BaseModel
from core.manager import AmzSkuMetricManager


class AmzSkuAdsMetric(BaseModel):
    date = models.DateField(auto_now_add=True)
    amz_sku = models.ForeignKey(AmzSku, on_delete=models.RESTRICT)
    opt_duration = models.IntegerField()
    revenue = models.FloatField()
    ads_revenue = models.FloatField()
    ratio = models.FloatField()
    manager = AmzSkuMetricManager()

    class Meta:
        unique_together = ('date', 'amz_sku', 'opt_duration')
        verbose_name_plural = "Amz SKU Ads Matric"