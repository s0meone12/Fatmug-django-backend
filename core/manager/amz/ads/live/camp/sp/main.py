from ......base import BaseManager


class SpCampManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__amz_sku = None
        self.__api = None

    @property
    def api(self):
        if self.__api is None:
            from .api import AmzAdsApiSubManagerSpCamp
            self.__api = AmzAdsApiSubManagerSpCamp(self)
        return self.__api

    @property
    def amz_sku(self):
        if self.__amz_sku is None:
            from .amz_sku import AmzSkuSubManagerSpCamp
            self.__amz_sku = AmzSkuSubManagerSpCamp(self)
        return self.__amz_sku
