from ........base import BaseManager


class SpNegativeTargetManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__api = None

    @property
    def api(self):
        if self.__api is None:
            from .api import AmzAdsApiSubManagerSpNegativeTarget
            self.__api = AmzAdsApiSubManagerSpNegativeTarget(self)
        return self.__api
