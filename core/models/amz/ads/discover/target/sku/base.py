from django.db import models
from .....sku import AmzSku
from ......inheritance import BaseModel


class BaseAmzSkuDiscTgt(BaseModel):
    sku = models.ForeignKey(AmzSku, on_delete=models.RESTRICT, null=False, blank=False)
    name = models.CharField(max_length=255, null=False, blank=False)
    clicks = models.IntegerField(null=False, blank=False, default=0)
    impressions = models.IntegerField(null=False, blank=False, default=0)
    cost = models.FloatField(null=False, blank=False, default=0)
    sales = models.FloatField(null=False, blank=False, default=0)

    class Meta:
        unique_together = ('sku', 'name')
        abstract = True