import pandas as pd
from core.models import Sku, AmzSku, SkuPriceAction
from .main import AmzSkuManager


class ViewSubManagerAmzSku:

    def __init__(self, manager: AmzSkuManager):
        self.manager = manager

    def __sync_sku(self):
        Sku.manager.odoo.sync()
        AmzSku.manager.odoo.sync()

    def get_price_recommendation(self, asins):
        self.__sync_sku()
        qs = self.manager.filter(asin__in=asins)
        self.manager.generate_recommended_sale_price(qs=qs)
        df = self.manager.filter(asin__in=asins).to_df(
            ['asin', 'sale_price', 'round_recommended_sale_price'])
        df = df.rename(columns={'sale_price': 'current_price',
                       'round_recommended_sale_price': 'recommended_price'})
        return df.to_dict(orient='records')

    def publish_price(self, asins):
        self.__sync_sku()
        qs = self.manager.filter(asin__in=asins)
        SkuPriceAction.manager.amz_sku.publish(qs=qs)
        df = SkuPriceAction.manager.amz_sku.get_last_submission(qs=qs)
        return df.to_dict(orient='records')
