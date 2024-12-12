from ......base import BaseManager


class SaleOrderRptManager(BaseManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__api = None
        self.__amz_sku = None

    @property
    def api(self):
        if not self.__api:
            from .amz_api import AmzApiSubManagerSaleOrderRpt
            self.__api = AmzApiSubManagerSaleOrderRpt(self)
        return self.__api

    @property
    def amz_sku(self):
        if not self.__amz_sku:
            from .amz_sku import AmzSkuSubManagerSaleOrderRpt
            self.__amz_sku = AmzSkuSubManagerSaleOrderRpt(self)
        return self.__amz_sku
