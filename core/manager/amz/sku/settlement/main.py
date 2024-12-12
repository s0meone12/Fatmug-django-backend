from core.manager.base import BaseManager


class AmzSkuSettlementManager(BaseManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__amz_sku = None

    @property
    def amz_sku(self):
        if not self.__amz_sku:
            from .sku import AmzSkuSubManagerAmzSkuSettlement
            self.__amz_sku = AmzSkuSubManagerAmzSkuSettlement(self)
        return self.__amz_sku
