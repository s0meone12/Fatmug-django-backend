from core.models.amz.ads import (
    SbKeyTgtAction,
    SpKeyTgtAction,
    SbProTgtAction,
    SpProTgtAction,
)
from core.models.amz.ads import (
    SpKeyTgtActionValues,
    SbKeyTgtActionValues,
    SbProTgtActionValues,
    SpProTgtActionValues,
)
from core.models.amz.ads import (
    SbKeyCampaignAction,
    SpKeyCampaignAction,
    SbProCampaignAction,
    SpProCampaignAction,
)
from core.models.amz.ads import (
    SbKeyCampaignActionValues,
    SpKeyCampaignActionValues,
    SbProCampaignActionValues,
    SpProCampaignActionValues,
)
from core.models.amz.ads.action.campaign.sp.key.intial_fetch import SpInitialFetchKeyCampaignAction
from core.models.amz.ads.action.campaign.sp.pro.intial_fetch import SpInitialFetchProCampaignAction
from django.db import transaction


class AmzAdsIndActionGenerator:

    def _run(self):
        """
        This method will generate the actions for the campaigns and targets.
        """
        self.generate_camp_action()
        self.generate_trgt_action()
    
    def generate_camp_action(self):
        """
        This method will store the action of updation of the live campaigns that do not require manual setup and save the actions in the database.
        values can be updated are: name, budget.
        """
        with transaction.atomic():
            # this update Camp Action
            SbKeyCampaignAction.manager.disc_campaign.campaign_update_action()
            SpKeyCampaignAction.manager.disc_campaign.campaign_update_action() 
            SbProCampaignAction.manager.disc_campaign.campaign_update_action() 
            SpProCampaignAction.manager.disc_campaign.campaign_update_action() 
            # SpInitialFetchKeyCampaignAction.manager.disc_fetch_camp.campaign_update_action()
            # SpInitialFetchProCampaignAction.manager.disc_fetch_camp.campaign_update_action()

            # this update Camp Action Values
            SbKeyCampaignActionValues.manager.action.campaign_update_action_values() 
            SpKeyCampaignActionValues.manager.action.campaign_update_action_values() 
            SbProCampaignActionValues.manager.action.campaign_update_action_values() 
            SpProCampaignActionValues.manager.action.campaign_update_action_values() 

    def generate_trgt_action(self):
        """
        This method will store the action of updation of the live targets and save the actions and also store action values in the database.
        values can be updated are: bid
        """
        with transaction.atomic():
            # this update Target Action
            SbKeyTgtAction.manager.disc_target.target_update_action() 
            SpKeyTgtAction.manager.disc_target.target_update_action()
            SbProTgtAction.manager.disc_target.target_update_action()
            SpProTgtAction.manager.disc_target.target_update_action()
        
        with transaction.atomic():
            # this update Target Action Values
            SbKeyTgtActionValues.manager.action.target_update_action_values()
            SpKeyTgtActionValues.manager.action.target_update_action_values()
            SbProTgtActionValues.manager.action.target_update_action_values()
            SpProTgtActionValues.manager.action.target_update_action_values()
