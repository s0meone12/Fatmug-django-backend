from ....base import BaseManager

class SkuPriceActionManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__amz_sku = None

    @property
    def amz_sku(self):
        if self.__amz_sku is None:
            from .amz_sku import AmzSkuSubManagerSkuPriceAction
            self.__amz_sku = AmzSkuSubManagerSkuPriceAction(self)
        return self.__amz_sku
