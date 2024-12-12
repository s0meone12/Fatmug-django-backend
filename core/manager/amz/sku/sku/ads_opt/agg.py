from core.models import Sku, AmzSku, SaleOrderRpt, AmzSbAdsCamp, AmzSdAdsCamp, AmzSpAdsCamp, AmzSbAdsTarget, AmzSdAdsTarget, AmzSpAdsTarget, AmzSbAdsKeyword, AmzSpAdsKeyword, AmzAdsPerformanceRptUpdate, AmzSpAdsNegativeKeyword, AmzSpAdsNegativeTarget
from .main import AdsOptSubManagerAmzSku


class AdsDataAggregationSubManagerAmzSku:
    def __init__(self, manager: AdsOptSubManagerAmzSku):
        self.manager = manager
    """
    Private methods not to be used directly.
    """

    def __agg_negative_targets(self):
        AmzSpAdsNegativeTarget.manager.api.sync()

    def __agg_positive_targets(self):
        AmzSbAdsTarget.manager.api.sync()
        AmzSdAdsTarget.manager.api.sync()
        AmzSpAdsTarget.manager.api.sync()

    def __agg_targets(self):
        self.__agg_negative_targets()
        self.__agg_positive_targets()

    def __agg_negative_keywords(self):
        AmzSpAdsNegativeKeyword.manager.api.sync()

    def __agg_positive_keywords(self):
        AmzSbAdsKeyword.manager.api.sync()
        AmzSpAdsKeyword.manager.api.sync()

    def __agg_keywords(self):
        self.__agg_negative_keywords()
        self.__agg_positive_keywords()

    def __agg_campaigns(self):
        AmzSbAdsCamp.manager.api.sync()
        AmzSdAdsCamp.manager.api.sync()
        AmzSpAdsCamp.manager.api.sync()

    def __agg_sales_rpt(self):
        SaleOrderRpt.manager.api.sync()

    def __agg_skus(self):
        Sku.manager.odoo.sync()
        AmzSku.manager.odoo.sync()

    def __agg_performance_rpt(self):
        AmzAdsPerformanceRptUpdate.manager.api.link_rpt()
        AmzAdsPerformanceRptUpdate.manager.api.get_rpt()
        AmzAdsPerformanceRptUpdate.manager.api.insert_rpt()

    def _run(self):
        self.__agg_skus()
        self.__agg_campaigns()
        self.__agg_targets()
        self.__agg_keywords()
        self.__agg_sales_rpt()
        self.__agg_performance_rpt()
