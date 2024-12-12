from django.db import models
from .. import AmzSkuDiscProTgt
from ... import SpDiscFetchKeyCamp
from .... import AmzSpAdsTarget
from ......inheritance import BaseModel
from core.manager import SpProFetchTgtDiscManager


class SPFetchProTgt(BaseModel):
    sku_disc_tgt = models.ForeignKey(
        AmzSkuDiscProTgt, on_delete=models.RESTRICT, unique=True)
    target_name = models.CharField(max_length=255, null=False, blank=False)
    disc_campaign = models.ForeignKey(
        SpDiscFetchKeyCamp, on_delete=models.RESTRICT, null=True)
    target = models.ForeignKey(
        AmzSpAdsTarget, on_delete=models.RESTRICT, unique=True, null=True)
    bid = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    muted_on = models.DateField(null=True, blank=True)
    unviable_on = models.DateField(null=True, blank=True)
    lifetime_spend = models.FloatField(null=True, blank=True)
    spend_since_mute = models.FloatField(null=True, blank=True, default=0)
    target_id_code = models.CharField(
        max_length=100, blank=True, null=True)

    manager = SpProFetchTgtDiscManager()

    class Meta:
        unique_together = ('sku_disc_tgt', 'disc_campaign', 'target_name')
