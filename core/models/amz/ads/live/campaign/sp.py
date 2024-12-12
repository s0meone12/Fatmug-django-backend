from django.db import models
from ....sku import AmzSku
from .....inheritance import BaseModel
from core.manager import SpCampManager


class AmzSpAdsCamp(BaseModel):
    amz_sku = models.ForeignKey(
        AmzSku, on_delete=models.RESTRICT, blank=True, null=True)
    budget = models.FloatField(null=False, blank=False)
    budget_type = models.CharField(max_length=100, null=False, blank=False, choices=[
        ('daily', 'Daily')])
    campaign_id_code = models.CharField(
        max_length=100, blank=False, null=False, unique=True)
    dynamic_bidding = models.CharField(max_length=255, null=False, blank=False)
    name = models.CharField(max_length=255, null=False, blank=False)
    start_date = models.DateField(null=False, blank=False)
    end_date = models.DateField(null=True, blank=True)
    state = models.CharField(max_length=100, choices=[(
        'enabled', 'Enabled'), ('paused', 'Paused'), ('archived', 'Archived')])
    targeting_type = models.CharField(max_length=100, choices=[
        ('manual', 'Manual'), ('auto', 'Auto')])
    manager = SpCampManager()