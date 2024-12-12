from django.db import models
from core.models.amz.ads.action.base import BaseAction
from core.models.amz.ads.discover.campaign.sp.fetch_pro_camp import SpDiscFetchProCamp
from core.manager.amz.ads.action.camp.sp.pro.fetch.main import SpProFetchCampActionManager


class SpInitialFetchProCampaignAction(BaseAction):
    disc_campaign = models.ForeignKey(
        SpDiscFetchProCamp, on_delete=models.RESTRICT, null=False, blank=False
    )
    manager = SpProFetchCampActionManager()
