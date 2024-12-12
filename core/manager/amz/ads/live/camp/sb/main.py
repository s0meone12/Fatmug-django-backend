from ......base import BaseManager


class SbCampManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__amz_sku = None
        self.__api = None

    @property
    def amz_sku(self):
        if self.__amz_sku is None:
            from .amz_sku import AmzSkuSubManagerSbCamp
            self.__amz_sku = AmzSkuSubManagerSbCamp(self)
        return self.__amz_sku

    @property
    def api(self):
        if self.__api is None:
            from .api import AmzAdsApiSubManagerSbCamp
            self.__api = AmzAdsApiSubManagerSbCamp(self)
        return self.__api
