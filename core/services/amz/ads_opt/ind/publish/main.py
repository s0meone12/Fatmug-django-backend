from core.models import SbKeyCampaignAction, SpKeyCampaignAction, SbProCampaignAction, SpProCampaignAction, SbKeyTgtAction, SpKeyTgtAction, SbProTgtAction, SpProTgtAction,SBDiscKeyCamp, SPDiscKeyCamp, SBDiscProCamp, SPDiscProCamp,SBDiscKeyTgt, SPDiscKeyTgt, SBDiscProTgt, SPDiscProTgt

class AmzAdsIndPublish:

    def __init__(self):
        pass

    def _run(self):
        # ******** Campaigns ********
        # Create campaigns
        SBDiscKeyCamp.manager.publish_create()
        SPDiscKeyCamp.manager.publish_create()
        SBDiscProCamp.manager.publish_create()
        SPDiscProCamp.manager.publish_create()

        # Update campaigns
        SbKeyCampaignAction.manager.publish_update()
        SbProCampaignAction.manager.publish_update()
        SpKeyCampaignAction.manager.publish_update()
        SpProCampaignAction.manager.publish_update()

        # Delete campaigns
        SBDiscKeyCamp.manager.publish_delete()
        SPDiscKeyCamp.manager.publish_delete()
        SBDiscProCamp.manager.publish_delete()
        SPDiscProCamp.manager.publish_delete()


        # ******** Targets ********
        # Create Key & Pro 
        SBDiscKeyTgt.manager.publish_create()
        SPDiscKeyTgt.manager.publish_create()
        SBDiscProTgt.manager.publish_create()
        SPDiscProTgt.manager.publish_create()

        # Update Key & Pro
        SbKeyTgtAction.manager.publish_update()
        SpKeyTgtAction.manager.publish_update()
        SbProTgtAction.manager.publish_update()
        SpProTgtAction.manager.publish_update()
