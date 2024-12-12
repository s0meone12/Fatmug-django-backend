from django.db import models
from ... import AmzSpAdsCamp
from ......inheritance import BaseModel
from core.manager import SpKeyManager

class AmzSpAdsKeyword(BaseModel):
    campaign = models.ForeignKey(AmzSpAdsCamp, on_delete=models.RESTRICT, null=False, blank=False)
    ad_group_id_code = models.CharField(max_length=100, blank=False, null=False)
    keyword_id_code = models.CharField(max_length=100, blank=False, null=False, unique=True)
    keyword_text = models.CharField(max_length=255, blank=False, null=False)
    match_type = models.CharField(max_length=100, choices=(
        ('broad', 'Broad'),
        ('exact', 'Exact'),
        ('phrase', 'Phrase'),
    ), blank=False, null=False)
    state = models.CharField(max_length=100, choices=(
        ('enabled', 'Enabled'),
        ('paused', 'Paused'),
        ('archived', 'Archived'),
    ), blank=False, null=False)
    bid = models.FloatField(blank=True, null=True, default=0.0)

    manager = SpKeyManager()