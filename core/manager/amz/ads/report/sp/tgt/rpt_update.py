from ......base import CheckQSMeta
from core.models import AmzAdsPerformanceRptUpdate
from ...base import BaseAmzAdsPerformanceRptUpdateSubManagerReportModdel
import re


class AmzAdsPerformanceRptUpdateSubManagerSpTgtReport(BaseAmzAdsPerformanceRptUpdateSubManagerReportModdel, metaclass=CheckQSMeta):

    def __init__(self, manager):
        self.manager = manager
        self.model = AmzAdsPerformanceRptUpdate

    def _transform_df(self, df):
        from core.models import AmzSpAdsTarget, AmzSpAdsKeyword
        target_list = [int(item[0]) for item in AmzSpAdsTarget.objects.all(
        ).values_list('target_id_code')]
        keyword_list = [int(item[0]) for item in AmzSpAdsKeyword.objects.all(
        ).values_list('keyword_id_code')]
        list_of_all_live_target = target_list + keyword_list

        # Why are we needing to check if the keywordId is in the list of all live target?
        df['is_in_list_of_all_live_target'] = df['keywordId'].isin(
            list_of_all_live_target)

        # Create a DataFrame for rows where is_in_list_of_all_live_target is False
        df_keywordId_not_present_in_db = df[df['is_in_list_of_all_live_target'] == False]

        # Create a DataFrame without the rows where is_in_list_of_all_live_target is False
        df = df[df['is_in_list_of_all_live_target'] == True]

        df['is_target'] = df['targeting'].apply(
            lambda x: bool(re.search(r'\w+=".*', x)) or x in ['close-match', 'loose-match', 'complements', 'substitutes'])
        # Apply conditions and create new columns
        df['targetId'] = df.apply(
            lambda row: row['keywordId'] if row['is_target'] else False, axis=1)
        df['keywordId'] = df.apply(
            lambda row: False if row['is_target'] else row['keywordId'], axis=1)
        # Convert back to integer type
        df['keywordId'] = df['keywordId'].astype('Int64')
        df['targetId'] = df['targetId'].astype('Int64')

        self._update_foreign_field_cols(df, {
            'targetId': 'target_id_code',
            'keywordId': 'keyword_id_code',
            'campaignId': 'campaign_id_code',
        })

        cols_to_rename = {
            'unitsSoldClicks14d': 'units_sold_clicks_14d',
            'attributedSalesSameSku14d': 'attributed_sales_same_sku_14d',
            'sales14d': 'sales_14d',
            'unitsSoldSameSku14d': 'units_sold_same_sku_14d',
        }
        df = df.rename(columns=cols_to_rename)
        df.drop(columns=['targeting', 'is_target',
                'is_in_list_of_all_live_target'], inplace=True)
        df['id'] = None
        return df

    def insert_rpt(self, qs=None):
        return self._insert_rpt(report_type='sp_tgt', qs=qs)
