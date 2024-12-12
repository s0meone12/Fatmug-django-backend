from core.models import AmzSku, AmzSbAdsKeyword, AmzSbAdsTarget, AmzSpAdsKeyword, AmzSpAdsTarget, AmzSdAdsTarget
from ......base import CheckQSMeta
from django.db.models import QuerySet
import pandas as pd


class AmzSkuSubManagerMixinAdCamp(metaclass=CheckQSMeta):

    def __init__(self, manager):
        self.manager = manager
        self.model = AmzSku

    def get_qs(self, qs=None) -> QuerySet:
        return self.manager.filter(amz_sku__in=qs)

    def _get_campaigns(self, type, qs=None) -> pd.DataFrame:
        qs = self.get_qs(qs=qs)
        if type == 'sb_keyword':
            qs = qs.filter(name__icontains='vdo').filter(name__icontains='key')
            print('SB Keyword Count: ', qs.count())
            df_adgroup = AmzSbAdsKeyword.manager.camp.get_adgroups(qs=qs)
        elif type == 'sb_target':
            qs = qs.filter(name__icontains='vdo').filter(name__icontains='pro')
            print('SB Target Count: ', qs.count())
            df_adgroup = AmzSbAdsTarget.manager.camp.get_adgroups(qs=qs)
        elif type == 'sd_target':
            print('SD Target Count: ', qs.count())
            df_adgroup = AmzSdAdsTarget.manager.camp.get_adgroups(qs=qs)
        elif type == 'sp_opt_keyword':
            qs = qs.filter(targeting_type='manual', name__icontains='key')
            print('SP Opt Keyword Count: ', qs.count())
            df_adgroup = AmzSpAdsKeyword.manager.camp.get_adgroups(qs=qs)
        elif type == 'sp_opt_target':
            qs = qs.filter(targeting_type='manual', name__icontains='pro').filter(name__icontains='opt')
            print('SP Opt Target Count: ', qs.count())
            df_adgroup = AmzSpAdsTarget.manager.camp.get_adgroups(qs=qs)
        elif type == 'sp_fetch_keyword':
            qs = qs.filter(targeting_type='auto')
            print('SP Fetch Keyword Count: ', qs.count())
            df_adgroup = AmzSpAdsTarget.manager.camp.get_adgroups(qs=qs)
        elif type == 'sp_fetch_target':
            qs = qs.filter(targeting_type='manual', name__icontains='pro').filter(name__icontains='fetch')
            print('SP Fetch Target Count: ', qs.count())
            df_adgroup = AmzSpAdsTarget.manager.camp.get_adgroups(qs=qs)
        else:
            raise ValueError(
                'Invalid type provided for get_valid_campaigns method in AmzSkuSubManagerMixinAdCamp')
        df_sku = qs.to_df(['id', 'amz_sku', 'name', 'budget', 'state', 'campaign_id_code']).rename(
            columns={'id': 'campaign'})
        print(df_sku.columns)
        print(df_adgroup.columns)
        # This needs to be checked. The validity of a campaign if it does not has any keyword is debatable.
        df = pd.merge(df_sku, df_adgroup, on='campaign', how='inner')
        # If campaign has multiple adgroups, then it is not valid, drop them. Remove those campaigns itself and not just drop the duplicates.
        print('Before Drop: ', df.shape[0])
        _df = df.drop_duplicates(subset=['campaign'], keep=False)
        print('After Drop: ', _df.shape[0])
        return _df
