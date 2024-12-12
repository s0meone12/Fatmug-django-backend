from ........base import BaseManager


class SpNegativeKeyManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__api = None

    @property
    def api(self):
        if self.__api is None:
            from .api import AmzAdsApiSubManagerSpNegativeKey
            self.__api = AmzAdsApiSubManagerSpNegativeKey(self)
        return self.__api
