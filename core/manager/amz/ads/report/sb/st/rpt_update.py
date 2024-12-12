from ......base import CheckQSMeta
from core.models import AmzAdsPerformanceRptUpdate
from ...base import BaseAmzAdsPerformanceRptUpdateSubManagerReportModdel


class AmzAdsPerformanceRptUpdateSubManagerSbStReport(BaseAmzAdsPerformanceRptUpdateSubManagerReportModdel, metaclass=CheckQSMeta):

    def __init__(self, manager):
        self.manager = manager
        self.model = AmzAdsPerformanceRptUpdate

    def _transform_df(self, df):
        self._update_foreign_field_cols(df, {
            'keywordId': 'keyword_id_code',
            'campaignId': 'campaign_id_code',
        })
        cols_to_rename = {
            'attributedSales14d': 'attributed_sales_14d',
        }
        df = df.rename(columns=cols_to_rename)
        df['id'] = None
        return df

    def insert_rpt(self, qs=None):
        return self._insert_rpt(report_type='sb_st', qs=qs)
