from core.manager.base import CheckQSMeta
from core.models import AmzSku, AmzSaleReturn, SaleOrderRpt
import pandas as pd
from django.db.models import F, Sum, Window
from .main import AmzSkuSaleReturnManager


class AmzSkuSubManagerAmzSkuSaleReturn(metaclass=CheckQSMeta):
    def __init__(self, manager: AmzSkuSaleReturnManager):
        self.manager = manager
        self.model = AmzSku
        self.days = 90

    def get_qs(self, qs=None):
        return self.manager.filter(sku__in=qs)

    def update_values(self, qs=None):
        df_return = AmzSaleReturn.manager.amz_sku.count(qs=qs)
        df_return_sku_total = df_return.groupby('sku').agg(
            count_return_total=('count', 'sum')).reset_index()[
            ['sku', 'count_return_total']]
        df_order = SaleOrderRpt.manager.amz_sku.count(qs=qs)
        df = pd.merge(df_order, df_return, on='sku',
                      how='outer', suffixes=('_order', '_return'))
        df = df[df['count_return'].notnull(
        ) & df['count_order'].notnull()]
        df = pd.merge(df, df_return_sku_total, on='sku',
                      how='left')
        df['total_return_percentage'] = df['count_return'] / \
            df['count_return_total']
        df['total_order_percentage'] = df['count_return'] / \
            df['count_order']
        df = df[['sku', 'detailed_disposition', 'total_return_percentage',
                 'total_order_percentage']]
        self.manager.dfdb.sync(df)

    def non_sellable(self, qs=None):
        qs = self.get_qs(qs=qs)
        return pd.DataFrame(qs.exclude(
            detailed_disposition__name='SELLABLE').annotate(
                percentage=Window(
                    expression=Sum('total_order_percentage'),
                    partition_by=[F('sku')],
                )
        ).distinct('sku').values('sku', 'percentage'))
