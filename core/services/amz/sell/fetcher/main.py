from .fulfillment import AmzSellFulfillmentFetcher
from .reports import AmzSellReportFetcher
from .base import AmzSellBaseFetcher


class AmzSellFetcher(AmzSellBaseFetcher):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reports = AmzSellReportFetcher()
        self.fulfillment = AmzSellFulfillmentFetcher()