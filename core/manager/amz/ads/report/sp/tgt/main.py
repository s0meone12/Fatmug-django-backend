from ......base import BaseManager
from django.db.models import Sum
import pandas as pd
from django.db.models import Q


class SpTgtReportManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__rpt_update = None

    @property
    def rpt_update(self):
        from .rpt_update import AmzAdsPerformanceRptUpdateSubManagerSpTgtReport
        if self.__rpt_update is None:
            self.__rpt_update = AmzAdsPerformanceRptUpdateSubManagerSpTgtReport(
                self)
        return self.__rpt_update
    
    def agg_pro_data_for_opt_period(self, qs=None):
        if qs is None:
            qs = self.model.objects.all()
        
        aggregated_data = qs.filter(
            keyword__isnull=True, 
            target__isnull=False, 
            target__expression_type='manual'
            ).exclude(
                Q(target__expression__icontains='ASIN_CATEGORY_SAME_AS') | 
                Q(target__expression__icontains='ASIN_EXPANDED_FROM')
                ).values('target').distinct().annotate(
                    _impressions=Sum('impressions'),
                    _clicks=Sum('clicks'),
                    spend=Sum('cost'),
                    sales=Sum('sales_14d')
                ).values('_impressions', '_clicks', 'spend', 'sales', 'target__target_id_code')

        df = pd.DataFrame(list(aggregated_data))
        return df
    
    def agg_key_data_for_opt_period(self, qs=None):
        if qs is None:
            qs = self.model.objects.all()
        
        aggregated_data = qs.filter(keyword__isnull=False, keyword__match_type='exact', target__isnull=True).values('keyword').distinct().annotate(
                    _impressions=Sum('impressions'),
                    _clicks=Sum('clicks'),
                    spend=Sum('cost'),
                    sales=Sum('sales_14d')
                ).values('_impressions', '_clicks', 'spend', 'sales', 'keyword__keyword_id_code')

        df = pd.DataFrame(list(aggregated_data))
        return df
