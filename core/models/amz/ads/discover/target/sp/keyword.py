from django.db import models
from .. import AmzSkuDiscKey
from ... import SPDiscKeyCamp
from .... import AmzSpAdsKeyword
from .....sku import AmzSku
from ......inheritance import BaseModel
from core.manager import SPDiscKeyTgtManager


class SPDiscKeyTgt(BaseModel):
    amz_sku = models.ForeignKey(
        AmzSku, on_delete=models.RESTRICT, null=False, blank=False)
    sku_disc_tgt = models.ForeignKey(
        AmzSkuDiscKey, on_delete=models.RESTRICT, unique=True)
    target_name = models.CharField(max_length=255, null=False, blank=False)
    disc_campaign = models.ForeignKey(
        SPDiscKeyCamp, on_delete=models.RESTRICT, null=True)
    keyword = models.ForeignKey(
        AmzSpAdsKeyword, on_delete=models.RESTRICT, unique=True, null=True)
    bid = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    muted_on = models.DateField(null=True, blank=True)
    unviable_on = models.DateField(null=True, blank=True)
    lifetime_spend = models.FloatField(null=True, blank=True)
    spend_since_mute = models.FloatField(null=True, blank=True, default=0)
    keyword_id_code = models.CharField(max_length=100, blank=True,unique=True, null=True)
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    manager = SPDiscKeyTgtManager()

    class Meta:
        unique_together = ('disc_campaign', 'target_name')
