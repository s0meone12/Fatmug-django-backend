from django.db import models
from ....sku import AmzSku
from .....inheritance import BaseModel
from core.manager import SbCampManager


class AmzSbAdsCamp(BaseModel):
    amz_sku = models.ForeignKey(
        AmzSku, on_delete=models.RESTRICT, blank=True, null=True)
    bidding = models.CharField(
        max_length=255, blank=False, null=False)
    brand_entity_id_code = models.CharField(
        max_length=100, null=True, blank=True)
    budget = models.FloatField(blank=False, null=False, default=0.0)
    budget_type = models.CharField(max_length=100, blank=False, null=False)
    campaign_id_code = models.CharField(
        max_length=100, blank=False, null=False, unique=True)
    cost_type = models.CharField(max_length=100, blank=False, null=False)
    goal = models.CharField(max_length=100, blank=False, null=False)
    is_multi_ad_groups_enabled = models.BooleanField(blank=False, null=False)
    name = models.CharField(max_length=100, null=False, blank=False)
    start_date = models.DateField(blank=False, null=False)
    state = models.CharField(max_length=100, blank=False, null=False, choices=[
        ('enabled', 'Enabled'), ('paused', 'Paused'), ('archived', 'Archived')])
    smart_default = models.CharField(max_length=100, blank=True, null=True)
    manager = SbCampManager()
