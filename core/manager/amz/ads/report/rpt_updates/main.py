from .....base import BaseManager


class AmzAdsPerformanceRptUpdateManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__api = None

    @property
    def api(self):
        if self.__api is None:
            from .api import AmzAdsApiSubManagerAmzAdsPerformanceRptUpdate
            self.__api = AmzAdsApiSubManagerAmzAdsPerformanceRptUpdate(
                self)
        return self.__api
