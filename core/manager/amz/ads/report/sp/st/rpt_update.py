from ......base import CheckQSMeta
from core.models import AmzAdsPerformanceRptUpdate
from ...base import BaseAmzAdsPerformanceRptUpdateSubManagerReportModdel



class AmzAdsPerformanceRptUpdateSubManagerSpStReport(BaseAmzAdsPerformanceRptUpdateSubManagerReportModdel, metaclass=CheckQSMeta):

    def __init__(self, manager):
        self.manager = manager
        self.model = AmzAdsPerformanceRptUpdate

    def _transform_df(self, df):
        self._update_foreign_field_cols(df, {
            'campaignId': 'campaign_id_code',
        })
        cols_to_rename = {
            'unitsSoldSameSku14d': 'units_sold_same_sku_14d',
            'attributedSalesSameSku14d': 'attributed_sales_same_sku_14d',
            'unitsSoldClicks14d': 'units_sold_clicks_14d',
            'sales14d': 'sales_14d',
        }
        df = df.rename(columns=cols_to_rename)
        df['id'] = None
        return df

    def insert_rpt(self, qs=None):
        return self._insert_rpt(report_type='sp_st', qs=qs)
