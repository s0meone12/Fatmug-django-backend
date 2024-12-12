from ........ import BaseManager


class SbProCampActionManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._disc_campaign = None
        self._publisher = None

    @property
    def disc_campaign(self):
        if not self._disc_campaign:
            from .disc_camp import SbProCampSubManagerSbProAction
            self._disc_campaign = SbProCampSubManagerSbProAction(self)
        return self._disc_campaign
    
    @property
    def publisher(self):
        from core.apis.clients import ADS_PUBLISHER
        if not self._publisher:
            self._publisher = ADS_PUBLISHER.AMZ_ADS_PUBLISHER_IN.sb
        return self._publisher
    
    def publish_update(self, qs=None):
        from core.models import SbProCampaignActionValues
        if qs is None:
            qs = self.all()
        action_qs = qs.filter(state="draft")
        df = SbProCampaignActionValues.manager.action.get_values(qs=action_qs)
        df_response = self.publisher.update_campaign(df)
        return self.dfdb.sync(df_response)
