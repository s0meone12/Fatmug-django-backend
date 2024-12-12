from django.db import models
from ... import AmzSpAdsCamp
from ......inheritance import BaseModel
from core.manager import SpNegativeKeyManager

class AmzSpAdsNegativeKeyword(BaseModel):
    campaign = models.ForeignKey(
        AmzSpAdsCamp, on_delete=models.RESTRICT, null=False, blank=False)
    ad_group_id_code = models.CharField(
        max_length=100, blank=False, null=True)
    keyword_id_code = models.CharField(
        max_length=100, blank=False, null=False, unique=True)
    keyword_text = models.CharField(max_length=255, blank=False, null=False)
    match_type = models.CharField(max_length=100, choices=(
        ('negative_exact', 'negative_exact'),
        ('negative_phrase', 'negative_phrase'),
    ), blank=False, null=False)
    state = models.CharField(max_length=100, choices=(
        ('enabled', 'Enabled'),
        ('paused', 'Paused'),
        ('archived', 'Archived'),
    ), blank=False, null=False)

    manager = SpNegativeKeyManager()