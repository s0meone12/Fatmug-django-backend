from core.services.amz.sell.data_agg import AmzSellDataAggregationService


class AmzSellService:
    def __init__(self):
        self.agg = AmzSellDataAggregationService()

    def aggregate_sales_data(self, *args, **kwargs):
        self.agg.aggregate_sales_data(*args, **kwargs)

    def aggregate_settlement_data(self, **kwargs):
        self.agg.aggregate_settlement_data(**kwargs)

    def aggregate_return_data(self, **kwargs):
        self.agg.aggregate_return_data(**kwargs)
