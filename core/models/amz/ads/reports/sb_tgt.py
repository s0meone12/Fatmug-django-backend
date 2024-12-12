from django.db import models
from .. import AmzSbAdsCamp, AmzSbAdsTarget
from ....inheritance import BaseModel
from core.manager import SbTgtReportManager


class AmzAdsSbTgtRpt(BaseModel):
    date = models.DateField(null=False, blank=False)
    campaign = models.ForeignKey(
        AmzSbAdsCamp, on_delete=models.RESTRICT, null=False, blank=False)
    target = models.ForeignKey(
        AmzSbAdsTarget, on_delete=models.RESTRICT, null=True, blank=True)
    impressions = models.IntegerField(null=False, blank=False, default=0)
    clicks = models.IntegerField(null=False, blank=False, default=0)
    cost = models.FloatField(null=False, blank=False, default=0)
    attributed_sales_14d = models.FloatField(
        null=False, blank=False, default=0)
    manager = SbTgtReportManager()