from core.manager.base import BaseManager
import pandas as pd


class AmzSkuManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__ads_opt = None
        self.__cron = None
        self.__odoo_cache = None
        self.__spapi = None
        self.__view = None

    @property
    def ads_opt(self):
        if self.__ads_opt is None:
            from .ads_opt import AdsOptSubManagerAmzSku
            self.__ads_opt = AdsOptSubManagerAmzSku(self)
        return self.__ads_opt

    @property
    def view(self):
        if self.__view is None:
            from .view import ViewSubManagerAmzSku
            self.__view = ViewSubManagerAmzSku(self)
        return self.__view

    @property
    def cron(self):
        if self.__cron is None:
            from .cron import CronSubManagerAmzSku
            self.__cron = CronSubManagerAmzSku(self)
        return self.__cron

    @property
    def odoo(self):
        if self.__odoo_cache is None:
            from .odoo_api import OdooApiSubManagerAmzSku
            self.__odoo_cache = OdooApiSubManagerAmzSku(self)
        return self.__odoo_cache

    @property
    def spapi(self):
        if self.__spapi is None:
            from .spapi import SpApiSubManagerAmzSku
            self.__spapi = SpApiSubManagerAmzSku(self)
        return self.__spapi

    def get_qs(self, qs=None):
        return qs

    def generate_recommended_sale_price(self, qs=None):
        def round_price(price):
            price = int(price)
            last_digit = price % 10
            return price - last_digit + 9
        from core.models import AmzSkuSettlement, AmzSkuSaleReturn
        qs = self.get_qs(qs=qs)
        df_sku = pd.DataFrame(qs.values('id', 'name', 'cost', 'tax_rate', 'mrp',
                                        'desired_profit', 'unit_ads_spend')).rename(columns={'id': 'sku'})
        df_sku_settlement = AmzSkuSettlement.manager.amz_sku.get_fees().rename(
            columns={'amount': 'fees'})
        df_sku_sale_return = AmzSkuSaleReturn.manager.amz_sku.non_sellable().rename(
            columns={'percentage': 'return_percentage'})
        df = pd.merge(df_sku, df_sku_settlement, on='sku', how='left').merge(
            df_sku_sale_return, on='sku', how='left')
        df['fees'] = df['fees'] * (-1)
        df['recommended_sale_price'] = ((df['cost'] +
                                         df['fees'] + df['unit_ads_spend'] +
                                         (df['return_percentage'] * df['cost'])) /
                                        (1 - df['desired_profit']/100)) * (1 + df['tax_rate'])
        df.fillna(-1, inplace=True)
        df['recommended_sale_price'] = df['recommended_sale_price'].astype(int)
        df.rename(columns={'sku': 'id'}, inplace=True)
        df = df[df['recommended_sale_price'] > 0]
        df['round_recommended_sale_price'] = df['recommended_sale_price'].apply(
            round_price)
        # If round_recommended_sale_price is greater than mrp, set it to mrp
        df['round_recommended_sale_price'] = df.apply(
            lambda x: x['mrp'] if x['round_recommended_sale_price'] > x['mrp'] else x['round_recommended_sale_price'], axis=1)
        df['recommended_sale_price'] = df.apply(
            lambda x: x['mrp'] if x['recommended_sale_price'] > x['mrp'] else x['recommended_sale_price'], axis=1)
        df = df[['id', 'recommended_sale_price', 'round_recommended_sale_price']]
        self.dfdb.sync(df)
