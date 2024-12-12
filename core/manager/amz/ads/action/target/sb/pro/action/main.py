from ........ import BaseManager
import pandas as pd


class SbProTargActionManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._disc_target = None
        self._publisher = None

    @property
    def disc_target(self):
        from .disc_target import SbProTargetSubManagerSbProAction
        if not self._disc_target:
            self._disc_target = SbProTargetSubManagerSbProAction(self)
        return self._disc_target
      
    @property
    def publisher(self):
        from core.apis.clients import ADS_PUBLISHER
        if not self._publisher:
            self._publisher = ADS_PUBLISHER.AMZ_ADS_PUBLISHER_IN.sb
        return self._publisher

    def publish_update(self, qs=None):
        if qs is None:
            qs = self.all()
        action_qs = qs.filter(state="draft").values("id","disc_target__bid" ,"disc_target__target_id_code" , "disc_target__disc_campaign__campaign_id_code", "disc_target__disc_campaign__adgroup_id_code")
        df = pd.DataFrame(list(action_qs))
        df_response = self.publisher.update_product_target_asin(df)
        return self.dfdb.sync(df_response)
