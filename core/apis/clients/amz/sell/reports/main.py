from .returns import SaleReturnReportFetcher
from .settlements import SaleSettlementReportFetcher
from .order import SaleOrderReportFetcher
from sp_api.base.marketplaces import Marketplaces
from .order import SaleOrderReportFetcher


class AmzSpApiReportFetcher:
    def __init__(self, marketplace: Marketplaces, *args, **kwargs):
        self.sale_return = SaleReturnReportFetcher(marketplace)
        self.settlement = SaleSettlementReportFetcher(marketplace)
        self.sale_order = SaleOrderReportFetcher(marketplace)
