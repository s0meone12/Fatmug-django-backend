from core.models import AmzSku, AmzAdsSpStRpt
from django.db.models import OuterRef, Subquery
import pandas as pd
from .......base import BaseManager


class AmzSkuSubManagerMixinAmzSkuDiscTgt:
    def __init__(self, manager: BaseManager):
        self.manager = manager
        self.model = AmzSku

    def get_qs(self, qs=None):
        return self.manager.filter(sku__in=qs)

    def _pending_discovery(self, qs=None, model=None):
        qs = self.get_qs(qs=qs)
        return qs.exclude(id__in=Subquery(model.manager.filter(
            sku_disc_tgt=OuterRef('pk')).values('sku_disc_tgt'))).to_df()

    def _discover_keywords(self, qs=None):
        return self._discover('keyword', qs=qs)

    def _discover_product_targets(self, qs=None):
        return self._discover('product', qs=qs)

    def _discover(self, target_type: str, qs=None):
        if target_type == 'keyword':
            rpt_df = AmzAdsSpStRpt.manager.amz_sku._read_unique_keyword_target_df(
                qs=qs)
        elif target_type == 'product':
            rpt_df = AmzAdsSpStRpt.manager.amz_sku._read_unique_product_target_df(
                qs=qs)
        else:
            raise ValueError(
                'target_type must be either "keyword" or "product')

        rpt_df.rename(columns={'campaign__amz_sku__name': 'sku',
                               'search_term': 'name',
                               'sales_14d': 'sales'}, inplace=True)

        sku_df = self.manager.all().to_df(['name', 'sku__name'])
        if sku_df.empty:
            sku_df = pd.DataFrame(columns=['name', 'sku__name'])
        sku_df.rename(columns={'sku__name': 'sku'}, inplace=True)

        # Perform a left merge to find entries in rpt_df that do not exist in sku_df
        merged_df = rpt_df.merge(
            sku_df, on=['sku', 'name'], how='left', indicator=True)

        # Filter out rows that have a match in sku_df
        df = merged_df[merged_df['_merge']
                       == 'left_only'].drop(columns='_merge')

        # Filtering only 'SKUs' in qs
        df = df[df['sku'].isin(pd.DataFrame(qs.values('name'))['name'])]

        # Prepare the 'sku' column for syncing
        df['sku'] = df['sku'].apply(lambda x: {
            'name': x})

        # Sync the filtered DataFrame
        return self.manager.dfdb.sync(df)
