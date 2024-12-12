from django.db import models
from ....sku import AmzSku
from .....inheritance import BaseModel
from core.manager import SdCampManager


class AmzSdAdsCamp(BaseModel):
    amz_sku = models.ForeignKey(
        AmzSku, on_delete=models.RESTRICT, blank=True, null=True
    )
    campaign_id_code = models.CharField(
        max_length=100, blank=False, null=False, unique=True
    )
    name = models.CharField(max_length=100, null=False, blank=False)
    tactic = models.CharField(max_length=100, null=False, blank=False)
    start_date = models.DateField(blank=False, null=False)
    state = models.CharField(
        max_length=100,
        blank=False,
        null=False,
        choices=[
            ("enabled", "Enabled"),
            ("paused", "Paused"),
            ("archived", "Archived"),
        ],
    )
    cost_type = models.CharField(
        max_length=100, blank=False, null=False, choices=[("cpc", "CPC")]
    )
    budget = models.FloatField(blank=False, null=False)
    budget_type = models.CharField(max_length=100, blank=False, null=False,  choices=[
        ('daily', 'Daily')])
    delivery_profile = models.CharField(max_length=100, null=False, blank=False, choices=[
        ('as_soon_as_possible', 'as_soon_as_possible')])

    manager = SdCampManager()
