from ........base import BaseManager


class SdTargetManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__camp = None
        self.__api = None

    @property
    def camp(self):
        if self.__camp is None:
            from .camp import AmzSdAdsCampSubManagerAmzSdAdsTarget
            self.__camp = AmzSdAdsCampSubManagerAmzSdAdsTarget(self)
        return self.__camp

    @property
    def api(self):
        if self.__api is None:
            from .api import AmzAdsApiSubManagerSdTarget
            self.__api = AmzAdsApiSubManagerSdTarget(self)
        return self.__api
