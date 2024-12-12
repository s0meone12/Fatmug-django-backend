from django.db import models
from ...base import BaseCampActionValues
from core.manager import SpProCampActionValueManager
from .action import SpProCampaignAction

class SpProCampaignActionValues(BaseCampActionValues):
    action = models.ForeignKey(
        SpProCampaignAction, on_delete=models.RESTRICT, null=False, blank=False
    )
    manager = SpProCampActionValueManager()

    class Meta:
        unique_together = ("action", "name")
