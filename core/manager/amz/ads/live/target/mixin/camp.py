import pandas as pd
from ......base import CheckQSMeta


class AdsCampSubManagerMixinAdsTarget(metaclass=CheckQSMeta):

    def __init__(self, manager, model):
        self.manager = manager
        self.model = model

    def get_qs(self, qs=None):
        return self.manager.filter(campaign__in=qs)

    def get_adgroups(self, qs=None) -> pd.DataFrame:
        qs = self.get_qs(qs=qs)
        return qs.distinct('campaign', 'ad_group_id_code').to_df(['campaign', 'ad_group_id_code'])
