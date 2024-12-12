from core.apis.clients import ADS_FETCHER

class PerformanceRptModelFetcher():
    def __init__(self):
        self.sb_client = ADS_FETCHER.AMZ_ADS_FETCHER_IN.sb
        self.sd_client = ADS_FETCHER.AMZ_ADS_FETCHER_IN.sd
        self.sp_client = ADS_FETCHER.AMZ_ADS_FETCHER_IN.sp

    def _get_report_id(self, report_type, date):
        if report_type == 'sb_tgt':
            return self.sb_client.post_report_v2_targeting(date)
        elif report_type == 'sb_st':
            return self.sb_client.post_report_v2_searchterm(date)
        elif report_type == 'sd_mt_at':
            return self.sd_client.post_report_v2_at_matched_target(date)
        elif report_type == 'sd_mt_ct':
            return self.sd_client.post_report_v2_ct_matched_target(date)
        elif report_type == 'sp_st':
            return self.sp_client.post_report_v3_searchterm(date)
        elif report_type == 'sp_tgt':
            return self.sp_client.post_report_v3_targeting(date)
        else:
            raise ValueError('Invalid report type')

    def _fetch_rpt_with_rpt_id(self, report_type, report_id):
        if report_type in ['sb_tgt', 'sb_st']:
            return self.sb_client._get_report_v2_from_id(report_id, report_client=self.sb_client._report_client)
        elif report_type in ['sd_mt_at', 'sd_mt_ct']:
            return self.sd_client._get_report_v2_from_id(report_id, report_client=self.sd_client._report_client)
        elif report_type in ['sp_st', 'sp_tgt']:
            return self.sp_client._get_report_v3_from_id(report_id, report_client=self.sp_client._report_client)
        else:
            raise ValueError('Invalid report type')

