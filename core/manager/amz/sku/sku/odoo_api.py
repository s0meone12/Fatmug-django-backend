from ....mixin import OdooApiSubManagerMixinSku
from .main import AmzSkuManager

class OdooApiSubManagerAmzSku(OdooApiSubManagerMixinSku):
    def __init__(self, manager: AmzSkuManager, fields=[
            'product_id',
            'sku_code',
            'asin',
            'is_discontinued',
            'fba_inv_days',
            'str_qc_re_rts_trns_fba_inv_days',
            'sale_price',
            'desired_ads_percentage',
            'unit_ads_spend',
            'product_cost',
            'product_tax_rate',
            'desired_profit_percentage',
            'to_publish_sale_price',
            'mrp',
    ]):
        super().__init__(fields)
        self.manager = manager

    def read(self, fields=[]):
        df = self._read_amz_sku(fields)
        df['product_id'] = df['product_id'].apply(
            lambda x: {'name': x} if x else {})
        df.rename(columns={
            'product_id': 'int_sku',
            'sku_code': 'name',
            'product_cost': 'cost',
            'product_tax_rate': 'tax_rate',
            'desired_profit_percentage': 'desired_profit'
        }, inplace=True)
        df['desired_profit'] = df['desired_profit']
        return df

    def sync(self):
        df = self.read()
        return self.manager.dfdb.sync(df)
