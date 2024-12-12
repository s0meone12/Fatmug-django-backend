from ......base import CheckQSMeta
from core.models import AmzAdsPerformanceRptUpdate
from ...base import BaseAmzAdsPerformanceRptUpdateSubManagerReportModdel


class AmzAdsPerformanceRptUpdateSubManagerSdMtReport(BaseAmzAdsPerformanceRptUpdateSubManagerReportModdel, metaclass=CheckQSMeta):

    def __init__(self, manager):
        self.manager = manager
        self.model = AmzAdsPerformanceRptUpdate

    def _transform_df(self, df):
        required_columns = ['matchedTarget', 'targetId', 'campaignId', 'attributedSales14d',
                            'impressions', 'clicks', 'cost', 'attributedUnitsOrdered14d', 'date', 'tactic_type']
        df = df[required_columns]

        self._update_foreign_field_cols(df, {
            'targetId': 'target_id_code',
            'campaignId': 'campaign_id_code',
        })
        cols_to_rename = {
            'attributedUnitsOrdered14d': 'attributed_units_ordered_14d',
            'attributedSales14d': 'attributed_sales_14d',
            'matchedTarget': 'matched_target'
        }
        df = df.rename(columns=cols_to_rename)
        df['id'] = None
        return df

    def insert_rpt(self, report_types=['sd_mt_at', 'sd_mt_ct'],  qs=None):
        for report_type in report_types:
            _qs = qs.filter(report_type=report_type)
            self._insert_rpt(report_type=report_type, qs=_qs)
