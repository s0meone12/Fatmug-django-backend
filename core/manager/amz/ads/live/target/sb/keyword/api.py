from ....mixin import AmzAdsApiSubManagerMixinSb
from ...mixin import AmzAdsApiSubManagerMixinAdsTarget
from .main import SbKeyManager


class AmzAdsApiSubManagerSbKey(AmzAdsApiSubManagerMixinAdsTarget, AmzAdsApiSubManagerMixinSb):
    def __init__(self, manager: SbKeyManager):
        self.manager = manager
        self.__client = None

    @property
    def client(self):
        if not self.__client:
            from core.apis.clients import ADS_FETCHER
            self.__client = ADS_FETCHER.AMZ_ADS_FETCHER_IN.sb
        return self.__client

    def read(self):
        df = self.client.list_keywords()
        df = self._filter_campaigns(df)
        df = self._transform_keywords_df(df)
        return df

    def sync(self):
        df = self.read()
        return self.manager.dfdb.sync(df)
