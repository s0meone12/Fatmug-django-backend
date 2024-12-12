from ........ import BaseManager

class SpProCampActionManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._disc_campaign = None
        self._publisher = None

    @property
    def publisher(self):
        from core.apis.clients import ADS_PUBLISHER
        if not self._publisher:
            self._publisher = ADS_PUBLISHER.AMZ_ADS_PUBLISHER_IN.sp
        return self._publisher
     
    @property
    def disc_campaign(self):
        from .disc_camp import SpProCampSubManagerSpProAction
        if not self._disc_campaign:
            self._disc_campaign = SpProCampSubManagerSpProAction(self)
        return self._disc_campaign       

    def publish_update(self, qs=None):
        from core.models import SpKeyCampaignActionValues
        if qs is None:
            qs = self.all()
        action_qs = qs.filter(state="draft")
        df = SpKeyCampaignActionValues.manager.action.get_values(qs=action_qs)# this will return req body for update
        df_response = self.publisher.update_campaign(df)
        return self.dfdb.sync(df_response) 
