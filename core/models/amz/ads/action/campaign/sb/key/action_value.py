from django.db import models
from . import SbKeyCampaignAction
from ...base import BaseCampActionValues
from core.manager import SbKeyCampActionValueManager


class SbKeyCampaignActionValues(BaseCampActionValues):
    action = models.ForeignKey(
        SbKeyCampaignAction, on_delete=models.RESTRICT, null=False, blank=False
    )
    manager = SbKeyCampActionValueManager()

    class Meta:
        unique_together = ("action", "name")