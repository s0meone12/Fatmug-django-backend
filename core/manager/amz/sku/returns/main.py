from core.manager.base import BaseManager


class AmzSkuSaleReturnManager(BaseManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__amz_sku = None

    @property
    def amz_sku(self):
        if not self.__amz_sku:
            from .amz_sku import AmzSkuSubManagerAmzSkuSaleReturn
            self.__amz_sku = AmzSkuSubManagerAmzSkuSaleReturn(self)
        return self.__amz_sku
