from django.db import models
from ...base import BaseCampActionValues
from core.manager import SbProCampActionValueManager
from .action import SbProCampaignAction

class SbProCampaignActionValues(BaseCampActionValues):
    action = models.ForeignKey(
        SbProCampaignAction, on_delete=models.RESTRICT, null=False, blank=False
    )
    manager = SbProCampActionValueManager()

    class Meta:
        unique_together = ("action", "name")
