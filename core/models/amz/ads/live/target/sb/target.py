from django.db import models
from ... import AmzSbAdsCamp
from ......inheritance import BaseModel
from core.manager import SbTargetManager

class AmzSbAdsTarget(BaseModel):
    campaign = models.ForeignKey(
        AmzSbAdsCamp, on_delete=models.RESTRICT, null=False, blank=False)
    target_id_code = models.CharField(
        max_length=100, blank=False, null=False, unique=True)
    ad_group_id_code = models.CharField(max_length=100, blank=False, null=False)
    state = models.CharField(max_length=100, choices=(
        ('enabled', 'Enabled'),
        ('paused', 'Paused'),
        ('archived', 'Archived'),
    ), blank=False, null=False)
    bid = models.FloatField(blank=True, null=True, default=0.0)
    expression = models.CharField(max_length=255, blank=False, null=True)
    resolved_expressions = models.CharField(
        max_length=255, blank=False, null=True)
    
    manager = SbTargetManager()
