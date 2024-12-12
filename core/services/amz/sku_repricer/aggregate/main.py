from core.models import Sku, AmzSku, AmzSettlement, AmzSaleReturn, AmzSkuSettlement


class AmzSkuRepricerAggregator:
    def run():
        Sku.manager.odoo.sync()
        AmzSku.manager.odoo.sync()
        AmzSaleReturn.manager.api.sync()
        AmzSettlement.manager.api.sync()
