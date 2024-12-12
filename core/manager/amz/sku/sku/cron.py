from core.models import Sku, AmzSku, AmzSaleReturn, AmzSettlement, SaleOrderRpt, AmzSkuSettlement, AmzSkuSaleReturn
from .main import AmzSkuManager


class CronSubManagerAmzSku:

    def __init__(self, manager: AmzSkuManager):
        self.manager = manager

    def reprice(self):
        Sku.manager.odoo.sync()
        AmzSku.manager.odoo.sync()
        SaleOrderRpt.manager.api.sync(from_days_ago=365)
        AmzSaleReturn.manager.api.sync(from_days_ago=365)
        AmzSettlement.manager.api.sync(from_days_ago=90)
        AmzSkuSettlement.manager.amz_sku.update_values()
        AmzSkuSaleReturn.manager.amz_sku.update_values()
        AmzSku.manager.generate_recommended_sale_price()
        AmzSku.manager.spapi.sync_sale_price()
        AmzSku.manager.spapi.sync_product_type()

    def optimize_ads(self):
        pass
