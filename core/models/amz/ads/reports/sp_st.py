from django.db import models
from .. import AmzSpAdsCamp
from ....inheritance import BaseModel
from core.manager import SpStReportManager


class AmzAdsSpStRpt(BaseModel):
    date = models.DateField(null=False, blank=False)
    campaign = models.ForeignKey(
        AmzSpAdsCamp, on_delete=models.RESTRICT, null=False, blank=False)
    search_term = models.CharField(max_length=255, null=False, blank=False)
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
    manager = SpStReportManager()
