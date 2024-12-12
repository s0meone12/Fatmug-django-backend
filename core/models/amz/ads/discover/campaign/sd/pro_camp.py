from django.db import models
from decimal import Decimal
from ......inheritance import BaseModel
from .... import AmzSdAdsCamp
from .....sku import AmzSku
from core.manager import AmzSdDiscProCampManager


class SDDiscProCamp(BaseModel):
    campaign = models.ForeignKey(
        AmzSdAdsCamp, null=True, blank=True, on_delete=models.DO_NOTHING)
    name = models.CharField(max_length=255, unique=True)
    budget = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal('500.0'))
    campaign_id_code = models.CharField(
        max_length=255, unique=True, blank=True, null=True)
    ad_group_id_code = models.CharField(
        max_length=255, unique=True, blank=True, null=True)
    ad_product_id_code = models.CharField(
        max_length=255, unique=True, blank=True, null=True)
    amz_sku = models.ForeignKey(
        AmzSku, on_delete=models.DO_NOTHING, blank=True, null=True)
    state = models.CharField(max_length=100, choices=[(
        'enabled', 'Enabled'), ('paused', 'Paused'), ('archived', 'Archived')])
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    message = models.TextField(null=True, blank=True)

    manager = AmzSdDiscProCampManager()
