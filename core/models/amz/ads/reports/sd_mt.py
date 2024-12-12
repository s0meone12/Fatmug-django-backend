from django.db import models
from .. import AmzSdAdsCamp, AmzSdAdsTarget
from ....inheritance import BaseModel
from core.manager import SdMtReportManager

class AmzAdsSdMtRpt(BaseModel):
    date = models.DateField(blank=False, null=False)
    campaign = models.ForeignKey(
        AmzSdAdsCamp, on_delete=models.RESTRICT, null=False, blank=False)
    target = models.ForeignKey(
        AmzSdAdsTarget, on_delete=models.RESTRICT, null=False, blank=False)
    matched_target = models.CharField(max_length=255, null=False, blank=False)
    impressions = models.IntegerField(null=False, blank=False, default=0)
    clicks = models.IntegerField(null=False, blank=False, default=0)
    cost = models.FloatField(null=False, blank=False, default=0)
    attributed_sales_14d = models.FloatField(
        null=False, blank=False, default=0)
    attributed_units_ordered_14d = models.IntegerField(
        null=False, blank=False, default=0)
    tactic_type = models.CharField(max_length=255, null=False, blank=False,choices=[(
        'ct', 'Contextual targeting'), ('at', 'Audiences targeting')])
    manager = SdMtReportManager()