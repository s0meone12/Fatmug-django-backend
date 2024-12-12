from django.db import models
from ......inheritance import BaseModel
from .. import AmzSkuDiscKey
from ... import SBDiscKeyCamp
from .... import AmzSbAdsKeyword
from .....sku import AmzSku
from core.manager import SBDiscKeyTgtManager


class SBDiscKeyTgt(BaseModel):
    amz_sku = models.ForeignKey(
        AmzSku, on_delete=models.RESTRICT, null=False, blank=False)
    sku_disc_tgt = models.ForeignKey(
        AmzSkuDiscKey, on_delete=models.RESTRICT, unique=True)
    disc_campaign = models.ForeignKey(
        SBDiscKeyCamp, on_delete=models.RESTRICT, null=True)
    keyword = models.ForeignKey(
        AmzSbAdsKeyword, on_delete=models.RESTRICT, unique=True, null=True, blank=True)
    bid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    muted_on = models.DateField(null=True, blank=True)
    unviable_on = models.DateField(null=True, blank=True)
    lifetime_spend = models.FloatField(null=True, blank=True)
    spend_since_mute = models.FloatField(null=True, blank=True, default=0)
    keyword_id_code = models.CharField(max_length=100, blank=True, null=True,unique=True)
    target_name = models.CharField(max_length=255, null=False, blank=False)
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    manager = SBDiscKeyTgtManager()

    class Meta:
        unique_together = ('disc_campaign', 'target_name')
