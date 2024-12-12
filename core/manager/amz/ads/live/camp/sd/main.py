from ......base import BaseManager


class SdCampManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__amz_sku = None
        self.__api = None

    @property
    def api(self):
        if self.__api is None:
            from .api import AmzAdsApiSubManagerSdCamp
            self.__api = AmzAdsApiSubManagerSdCamp(self)
        return self.__api

    @property
    def amz_sku(self):
        if self.__amz_sku is None:
            from .amz_sku import AmzSkuSubManagerSdCamp
            self.__amz_sku = AmzSkuSubManagerSdCamp(self)
        return self.__amz_sku
