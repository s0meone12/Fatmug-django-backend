from ........base import BaseManager


class SpTargetManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__camp = None
        self.__api = None

    @property
    def camp(self):
        if self.__camp is None:
            from .camp import AmzSpAdsCampSubManagerAmzSpAdsTarget
            self.__camp = AmzSpAdsCampSubManagerAmzSpAdsTarget(self)
        return self.__camp

    @property
    def api(self):
        if self.__api is None:
            from .api import AmzAdsApiSubManagerSpTarget
            self.__api = AmzAdsApiSubManagerSpTarget(self)
        return self.__api
