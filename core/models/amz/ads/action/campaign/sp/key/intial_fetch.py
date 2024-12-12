from django.db import models
from ....base import BaseAction
from ..... import SpDiscFetchKeyCamp
from core.manager import SpKeyFetchCampActionManager


class SpInitialFetchKeyCampaignAction(BaseAction):
    disc_campaign = models.ForeignKey(
        SpDiscFetchKeyCamp, on_delete=models.RESTRICT, null=False, blank=False
    )
    manager = SpKeyFetchCampActionManager()
