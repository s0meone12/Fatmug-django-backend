from ....mixin import AmzAdsApiSubManagerMixinAdsTarget
from .main import SpNegativeTargetManager


class AmzAdsApiSubManagerSpNegativeTarget(AmzAdsApiSubManagerMixinAdsTarget):

    def __init__(self, manager: SpNegativeTargetManager):
        self.manager = manager
        self.__client = None

    @property
    def client(self):
        if not self.__client:
            from core.apis.clients import ADS_FETCHER
            self.__client = ADS_FETCHER.AMZ_ADS_FETCHER_IN.sp
        return self.__client

    def read(self):
        df = self.client.list_negative_targets()
        df = self._transform_targets_df(df)
        return df

    def sync(self):
        df = self.read()
        return self.manager.dfdb.sync(df)
