from ....base import BaseAction
from ..... import SPDiscKeyCamp
from django.db import models
from core.manager import SpKeyCampActionManager


class SpKeyCampaignAction(BaseAction):
    disc_campaign = models.ForeignKey(
        SPDiscKeyCamp, on_delete=models.RESTRICT, null=False, blank=False
    )
    manager = SpKeyCampActionManager()
