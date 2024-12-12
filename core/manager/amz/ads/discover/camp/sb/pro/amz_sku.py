import pandas as pd
from .......base import CheckQSMeta
from core.models import SBDiscProTgt, AmzSku
from django.db.models import Count, F, Window
from .main import AmzSbDiscProCampManager


class AmzSkuSubManagerSbDiscProCamp(metaclass=CheckQSMeta):
    def __init__(self, manager: AmzSbDiscProCampManager):
        self.manager = manager
        self.model = AmzSku

    def get_qs(self, qs=None):
        return self.manager.filter(amz_sku__in=qs)

    def no_of_live_campaigns(self, qs=None) -> pd.DataFrame:
        """
        Fetch existing campaigns with count of keywords/targets currently associated
        """
        qs = self.get_qs(qs=qs)
        df = qs.filter(campaign__isnull=False).annotate(
            count=Window(expression=Count('campaign'), partition_by=[F('amz_sku')])).distinct('amz_sku').values('amz_sku', 'count').to_df()
        if df.empty:
            return pd.DataFrame(columns=['amz_sku', 'count'])
        return df

    def no_of_live_targets(self, qs=None) -> pd.DataFrame:
        """
        Fetch existing campaigns with count of keywords/targets currently associated
        """
        qs = self.get_qs(qs=qs)
        df = SBDiscProTgt.manager.camp.no_of_live_targets(
            qs=qs.filter(campaign__isnull=False))
        if df.empty:
            return pd.DataFrame(columns=['amz_sku', 'count'])
        df = df[['amz_sku_id', 'count']]
        return df.groupby('amz_sku_id').sum().reset_index()

    def no_of_targets_pending_campaign_addition(self, qs=None) -> int:
        """
        This method will count the number of new discovery for the sku
        """
        discovered_keyword_targets = SBDiscProTgt.manager.filter(
            target__isnull=True, disc_campaign__isnull=True,
            sku_disc_tgt__sku__in=qs).count()
        return discovered_keyword_targets

    def __generate_new_names(self, qs=None) -> list[str]:
        names = []
        for qs_i in qs:
            new_disc_trgt_count = self.no_of_targets_pending_campaign_addition(
                qs=qs_i)
            if new_disc_trgt_count == 0:
                continue
            x = self.no_of_live_campaigns(qs=qs_i)
            num_live_campaign = x['count'].values[0] if not x.empty else 0
            y = self.no_of_live_targets(qs=qs_i)
            num_keywords_in_live_campaign = y['count'].values[0] if not y.empty else 0
            empty_space_in_live_camp = num_live_campaign * \
                1000 - num_keywords_in_live_campaign

            if new_disc_trgt_count > empty_space_in_live_camp:
                remainder = (new_disc_trgt_count -
                             empty_space_in_live_camp) % 1000
                num_of_new_camps_required = (
                    new_disc_trgt_count - empty_space_in_live_camp) // 1000
                if remainder > 0:
                    num_of_new_camps_required += 1
            else:
                num_of_new_camps_required = 0

            # Generate names for the new campaigns following a specific naming convention
            for i in range(num_of_new_camps_required):
                initial_letter_for_camp_name = num_live_campaign + 1 + i
                name = f"{initial_letter_for_camp_name}^Vdo_{qs_i.int_sku.name}_{qs_i.asin}_Pro"
                names.append({"name": name, "budget": 500,
                             "amz_sku_id": {"name": qs_i.name}})
        return names

    def discover(self, qs=None):
        data = self.__generate_new_names(qs=qs)
        df = pd.DataFrame(data)
        if not df.empty:
            self.manager.dfdb.sync(df)
