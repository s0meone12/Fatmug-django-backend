from .......base import BaseManager


class AmzSkuDiscProTgtManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__amz_sku = None

    @property
    def amz_sku(self):
        if not self.__amz_sku:
            from .amz_sku import AmzSkuSubManagerAmzSkuDiscProTgt
            self.__amz_sku = AmzSkuSubManagerAmzSkuDiscProTgt(self)
        return self.__amz_sku
