from .......base import CheckQSMeta
from core.models import SPDiscProCamp
import pandas as pd
from django.db.models import Count, F, Window


class SpProCampSubManagerTarget(metaclass=CheckQSMeta):
    def __init__(self, manager):
        self.manager = manager
        self.model = SPDiscProCamp
        # self.bulk = BulkSubManagerTarget() -> DataFrame
   
    def get_qs(self, qs=None):
        return self.manager.filter(disc_campaign__in=qs)

    def no_of_live_targets(self, qs=None) -> pd.DataFrame:
        qs = self.get_qs(qs=qs)
        df = qs.filter(target__isnull=False).annotate(count=Window(expression=Count('target'), partition_by=[
            F('disc_campaign')])).distinct('disc_campaign').values('amz_sku', 'disc_campaign', 'count').to_df()
        if df.empty:
            df = pd.DataFrame(columns=['amz_sku', 'disc_campaign', 'count'])
        return df

    def empty_space_in_live_camp(self, qs) -> int:
        df = self.no_of_live_targets(qs=qs)
        df['count'] = 1000 - df['count']
        # If any count is negative, then raise an error
        if df['count'].lt(0).any():
            raise ValueError(
                "Negative values found in empty_space_in_live_camp")
        return df
    