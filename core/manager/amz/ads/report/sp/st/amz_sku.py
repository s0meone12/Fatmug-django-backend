from core.models import AmzSku
import pandas as pd


class AmzSkuSubManagerSpStReport:

    def __init__(self, manager):
        self.manager = manager
        self.model = AmzSku

    def get_qs(self, qs=None):
        return self.manager.filter(campaign__amz_sku__in=qs)

    def __read_unique_target_df(self, target_type, qs=None):
        qs = self.get_qs(qs=qs)
        if target_type == 'product':
            qs = qs.filter(search_term__iregex=r'b0[0-9a-zA-Z]{8}')
        elif target_type == 'keyword':
            qs = qs.exclude(search_term__iregex=r'b0[0-9a-zA-Z]{8}')
        else:
            raise ValueError(
                'target_type must be either "product" or "keyword"')
        df = pd.DataFrame.from_records(qs.values(
            'search_term', 'campaign__amz_sku__name', 'impressions', 'clicks', 'cost', 'sales_14d'))
        df = df.groupby(['search_term', 'campaign__amz_sku__name']).agg(
            {'impressions': 'sum', 'clicks': 'sum', 'cost': 'sum', 'sales_14d': 'sum'}).reset_index()
        return df

    def _read_unique_product_target_df(self, qs=None):
        return self.__read_unique_target_df('product', qs=qs)

    def _read_unique_keyword_target_df(self, qs=None):
        return self.__read_unique_target_df('keyword', qs=qs)
