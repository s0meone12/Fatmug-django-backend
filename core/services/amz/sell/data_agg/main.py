from core.services.amz.sell.data_agg.reports import AmzSellReportDataAggregationService


class AmzSellDataAggregationService:
    def __init__(self):
        self.report_agg = AmzSellReportDataAggregationService()

    def aggregate_sales_data(self, *args, **kwargs):
        self.report_agg._sync_sales_orders(*args, **kwargs)

    def aggregate_settlement_data(self, **kwargs):
        self.report_agg._sync_order_settlement_reports(**kwargs)

    def aggregate_return_data(self, **kwargs):
        self.report_agg._sync_amz_return_reports(**kwargs)

    def aggregate_amz_sku_sale_price_data(self, **kwargs):
        return self.report_agg._sync_amz_sku_sale_price_data(**kwargs)

    def aggregate_amz_sku_product_type_data(self, **kwargs):
        return self.report_agg._sync_amz_sku_product_type_data(**kwargs)
