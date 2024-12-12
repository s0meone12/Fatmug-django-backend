from ......base import BaseManager
import pandas as pd


class AmzSkuDiscTargetBaseManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def _model_sp_st_rpt(self):
        from core.models import AmzAdsSpStRpt
        return AmzAdsSpStRpt

    def _discover(self, target_type: str):
        if target_type == 'keyword':
            rpt_df = self._model_sp_st_rpt.manager._read_unique_keyword_target_df()
        elif target_type == 'product':
            rpt_df = self._model_sp_st_rpt.manager._read_unique_product_target_df()
        else:
            raise ValueError(
                'target_type must be either "keyword" or "product')
        
        rpt_df.rename(columns={'campaign__amz_sku__name': 'sku',
                               'search_term': 'name',
                               'sales_14d': 'sales'}, inplace=True)
        sku_df = pd.DataFrame.from_records(self.all().values('name', 'sku__name'))
        sku_df.rename(columns={'sku__name': 'sku'}, inplace=True)
        # Create temporary DataFrames for comparison
        rpt_df_temp = rpt_df[['sku', 'name']]
        sku_df_temp = sku_df[['sku', 'name']]
        # Find new search_terms
        new_search_terms_temp = rpt_df_temp[~rpt_df_temp.isin(
            sku_df_temp)].dropna()
        
        # Filter the original DataFrame
        rpt_df = rpt_df[rpt_df_temp.isin(new_search_terms_temp).all(axis=1)]
        rpt_df['sku'] = rpt_df['sku'].apply(lambda x: {'name': x})
        print(rpt_df)
        return self.dfdb.sync(rpt_df)
