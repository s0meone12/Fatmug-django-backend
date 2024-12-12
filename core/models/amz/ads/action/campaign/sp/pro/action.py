from django.db import models
from ....base import BaseAction
from ..... import SPDiscProCamp
from core.manager import SpProCampActionManager


class SpProCampaignAction(BaseAction):
    disc_campaign = models.ForeignKey(
        SPDiscProCamp, on_delete=models.RESTRICT, null=False, blank=False
    )
    manager = SpProCampActionManager()


