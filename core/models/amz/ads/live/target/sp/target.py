from django.db import models
from ... import AmzSpAdsCamp
from ......inheritance import BaseModel
from core.manager import SpTargetManager


class AmzSpAdsTarget(BaseModel):
    campaign = models.ForeignKey(
        AmzSpAdsCamp, on_delete=models.RESTRICT, null=False, blank=False)
    ad_group_id_code = models.CharField(
        max_length=100, blank=False, null=False)
    expression = models.CharField(max_length=255, blank=False, null=False)
    expression_type = models.CharField(max_length=100, choices=(
        ('auto', 'Auto'),
        ('manual', 'Manual'),
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
    bid = models.FloatField(blank=True, null=True, default=0.0)

    manager = SpTargetManager()
