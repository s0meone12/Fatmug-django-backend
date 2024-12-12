from .base import AmzSellFullFillmentBaseDataAggregationService
from core.services.amz.sell.fetcher import AmzSellFetcher


class AmzSellFulFillmentDataAggregationService(AmzSellFullFillmentBaseDataAggregationService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.amz_sell_fulfillment_fetcher = AmzSellFetcher().fulfillment