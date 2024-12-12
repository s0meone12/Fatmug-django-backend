from django.db import models
from ... import AmzSbAdsCamp
from ......inheritance import BaseModel
from core.manager import SbKeyManager


class AmzSbAdsKeyword(BaseModel):
    KN_NAME_FIELD = "keyword_text"
    campaign = models.ForeignKey(
        AmzSbAdsCamp, on_delete=models.RESTRICT, null=False, blank=False)
    keyword_id_code = models.CharField(
        max_length=100, blank=False, null=False, unique=True)
    ad_group_id_code = models.CharField(
        max_length=100, blank=False, null=False)
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

    manager = SbKeyManager()
