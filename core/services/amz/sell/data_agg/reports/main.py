from datetime import datetime
from .base import AmzSellReportsBaseDataAggregationService
from core.models import SaleOrderRpt, AmzSku
from core.services.amz.sell.fetcher import AmzSellFetcher
from core.models.amz.sell.reports.sale.settlements import (
    AmzSettlement,
    AmzSettlementDetail,
)
from core.models.amz.sell.reports.sale.returns import AmzSaleReturn


class AmzSellReportDataAggregationService(AmzSellReportsBaseDataAggregationService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.amz_sell__fetcher = AmzSellFetcher()

    def _sync_sales_orders(self, *args, **kwargs):
        from_date_time = kwargs.get("from_date_time", None)
        to_date_time = datetime.now().date()
        sales_df = self.amz_sell__fetcher.reports.sales_orders(
            dataStartTime=from_date_time, dataEndTime=to_date_time
        )
        print(f"len(sales_df): {len(sales_df)}")
        df = self._transform_sell_order_rpt_columns(df=sales_df)
        print(f"len(df): {len(df)}")
        sku_name_list = list(
            AmzSku.objects.all().values_list("name", flat=True))
        print(f"len(sku_name_list): {len(sku_name_list)}")
        filtered_df = df[df["sku"].apply(lambda x: x["name"] in sku_name_list)]
        print(f"len(filtered_df): {len(filtered_df)}")
        SaleOrderRpt.dfdb.sync(df=filtered_df)

    def _sync_order_settlement_reports(self, **kwargs):

        df = self.amz_sell__fetcher.reports.amz_settlement(**kwargs)

        amz_settlement_df = self._transform_amz_settlement_rpt_columns(
            df.copy())
        AmzSettlement.dfdb.sync(df=amz_settlement_df)

        amz_settlement_detail_df = self._transform_amz_settlement_detail_rpt_columns(
            df)
        AmzSettlementDetail.dfdb.sync(
            df=amz_settlement_detail_df)

    def _sync_amz_return_reports(self, **kwargs):

        df = self.amz_sell__fetcher.reports.amz_returns(**kwargs)
        amz_return_df = self._transform_amz_return_rpt_columns(df)
        AmzSaleReturn.dfdb.sync(df=amz_return_df)

    def _sync_amz_sku_sale_price_data(self, **kwargs):
        import asyncio

        loop = asyncio.get_event_loop()
        df = loop.run_until_complete(
            self.amz_sell__fetcher.reports.amz_sku_sale_price(
                skus=list(AmzSku.objects.all().values_list("name", flat=True)), **kwargs
            )
        )
        print(df)
        if not df is None:
            AmzSku.dfdb.sync(df=df)
            return len(df)

    def _sync_amz_sku_product_type_data(self, **kwargs):
        import asyncio

        loop = asyncio.get_event_loop()
        df = loop.run_until_complete(
            self.amz_sell__fetcher.reports.amz_sku_product_type(
                sku_names=list(
                    AmzSku.objects.all().values_list("name", flat=True))
            )
        )
        if not df is None:
            AmzSku.dfdb.sync(df=df)
            return len(df)
