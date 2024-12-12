from ......base import BaseManager


class AmzSaleReturnManager(BaseManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__api = None
        self.__amz_sku = None

    @property
    def amz_sku(self):
        if not self.__amz_sku:
            from .amz_sku import AmzSkuSubManagerAmzSaleReturn
            self.__amz_sku = AmzSkuSubManagerAmzSaleReturn(self)
        return self.__amz_sku

    @property
    def api(self):
        if not self.__api:
            from .api import ApiSubManagerAmzSaleReturn
            self.__api = ApiSubManagerAmzSaleReturn(self)
        return self.__api
