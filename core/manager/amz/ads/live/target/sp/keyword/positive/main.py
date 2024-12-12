from ........base import BaseManager


class SpKeyManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__camp = None
        self.__api = None

    @property
    def camp(self):
        if self.__camp is None:
            from .camp import AmzSpAdsCampSubManagerAmzSpAdsKeyword
            self.__camp = AmzSpAdsCampSubManagerAmzSpAdsKeyword(self)
        return self.__camp

    @property
    def api(self):
        if self.__api is None:
            from .api import AmzAdsApiSubManagerSpKey
            self.__api = AmzAdsApiSubManagerSpKey(self)
        return self.__api
