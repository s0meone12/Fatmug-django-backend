from ......base import BaseManager
from django.db.models import Sum
import pandas as pd


class SbStReportManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__rpt_update = None

    @property
    def rpt_update(self):
        from .rpt_update import AmzAdsPerformanceRptUpdateSubManagerSbStReport
        if self.__rpt_update is None:
            self.__rpt_update = AmzAdsPerformanceRptUpdateSubManagerSbStReport(
                self)
        return self.__rpt_update
    
    def agg_data_for_opt_period(self, qs=None)->pd.DataFrame:
        if qs is None:
            qs = self.all()
        aggregated_data = qs.filter(keyword__isnull= False, keyword__match_type='exact').values('keyword').distinct().annotate(
                    _impressions=Sum('impressions'),
                    _clicks=Sum('clicks'),
                    spend=Sum('cost'),
                    sales=Sum('attributed_sales_14d')
                ).values('_impressions', '_clicks', 'spend', 'sales', 'keyword__keyword_id_code')

        df = pd.DataFrame(list(aggregated_data))
        return df