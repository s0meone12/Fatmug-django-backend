from django.db import models
from ... import AmzSdAdsCamp
from ......inheritance import BaseModel
from core.manager import SdTargetManager

class AmzSdAdsTarget(BaseModel):
    campaign = models.ForeignKey(AmzSdAdsCamp, on_delete=models.RESTRICT, null=False, blank=False)
    ad_group_id_code = models.CharField(max_length=100, blank=False, null=False)
    bid = models.FloatField(blank=True, null=True, default=0.0)
    expression = models.CharField(max_length=255, blank=False, null=False)
    expression_type = models.CharField(max_length=100, choices=(
        ('manual', 'Manual'),
        ('auto', 'Auto'),
    ), blank=False, null=False)
    resolved_expression = models.CharField(
        max_length=255, blank=False, null=False)
    state = models.CharField(max_length=100, choices=(
        ('enabled', 'Enabled'),
        ('paused', 'Paused'),
        ('archived', 'Archived'),
    ), blank=False, null=False)
    target_id_code = models.CharField(
        max_length=100, blank=False, null=False, unique=True)

    manager = SdTargetManager()