from django.db import models
from ....inheritance import BaseModel
from .. import AmzSpAdsCamp, AmzSpAdsTarget, AmzSpAdsKeyword
from core.manager import SpTgtReportManager


class AmzAdsSpTgtRpt(BaseModel):
    date = models.DateField(null=False, blank=False)
    campaign = models.ForeignKey(
        AmzSpAdsCamp, on_delete=models.RESTRICT, null=False, blank=False)
    keyword = models.ForeignKey(
        AmzSpAdsKeyword, on_delete=models.RESTRICT, null=True, blank=True)
    target = models.ForeignKey(
        AmzSpAdsTarget, on_delete=models.RESTRICT, null=True, blank=True)
    impressions = models.IntegerField(null=False, blank=False, default=0)
    clicks = models.IntegerField(null=False, blank=False, default=0)
    cost = models.FloatField(null=False, blank=False, default=0)
    sales_14d = models.FloatField(null=False, blank=False, default=0)
    units_sold_clicks_14d = models.IntegerField(
        null=False, blank=False, default=0)
    attributed_sales_same_sku_14d = models.FloatField(
        null=False, blank=False, default=0)
    units_sold_same_sku_14d = models.IntegerField(
        null=False, blank=False, default=0)
    manager = SpTgtReportManager()