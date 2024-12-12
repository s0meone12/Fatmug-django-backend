from django.db import models
from ..... import SBDiscKeyCamp
from ....base import BaseAction
from core.manager import SbKeyCampActionManager


class SbKeyCampaignAction(BaseAction):
    disc_campaign = models.ForeignKey(
        SBDiscKeyCamp, on_delete=models.RESTRICT, null=False, blank=False
    )
    manager = SbKeyCampActionManager()
