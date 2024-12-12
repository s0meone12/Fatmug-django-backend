from django.db import models
from ..... import SBDiscProCamp
from ....base import BaseAction
from core.manager import SbProCampActionManager


class SbProCampaignAction(BaseAction):
    disc_campaign = models.ForeignKey(
        SBDiscProCamp, on_delete=models.RESTRICT, null=False, blank=False
    )
    manager = SbProCampActionManager()
