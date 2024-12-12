from ......base import BaseManager
from django.db.models import Sum
import pandas as pd

class SbTgtReportManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__rpt_update = None

    @property
    def rpt_update(self):
        from .rpt_update import AmzAdsPerformanceRptUpdateSubManagerSbTgtReport
        if self.__rpt_update is None:
            self.__rpt_update = AmzAdsPerformanceRptUpdateSubManagerSbTgtReport(
                self)
        return self.__rpt_update
    
    def agg_data_for_opt_period(self, qs=None)->pd.DataFrame:
        if qs is None:
            qs = self.all()
        aggregated_data = qs.filter(target__isnull= False).values('target').distinct().annotate(
                    _impressions=Sum('impressions'),
                    _clicks=Sum('clicks'),
                    spend=Sum('cost'),
                    sales=Sum('attributed_sales_14d')
                ).values('_impressions', '_clicks', 'spend', 'sales', 'target__target_id_code')

        df = pd.DataFrame(list(aggregated_data))
        return df
