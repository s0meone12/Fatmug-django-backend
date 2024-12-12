from django.db import models
from ...base import BaseCampActionValues
from core.manager import SpKeyCampActionValueManager
from .action import SpKeyCampaignAction


class SpKeyCampaignActionValues(BaseCampActionValues):
    action = models.ForeignKey(
        SpKeyCampaignAction, on_delete=models.RESTRICT, null=False, blank=False
    )
    manager = SpKeyCampActionValueManager()

    class Meta:
        unique_together = ("action", "name")