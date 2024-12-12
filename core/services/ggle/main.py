from .data_agg import GoogleAmzAmdsDataAggregationService


class Ggle:

    def __init__(self, *args, **kwargs):
        self.amz_ads_data_agg = GoogleAmzAmdsDataAggregationService()

    def sync_amz_ads_performance_report_updates(self):
        try:
            self.amz_ads_data_agg._sync_amz_ads_performance_report_updates()
        except Exception as e:
            raise Exception(
                'Error syncing amz ads performance report updates from Google Drive: {}'.format(str(e)))
