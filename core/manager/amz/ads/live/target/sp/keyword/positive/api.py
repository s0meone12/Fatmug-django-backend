from ....mixin import AmzAdsApiSubManagerMixinAdsTarget
from .main import SpKeyManager


class AmzAdsApiSubManagerSpKey(AmzAdsApiSubManagerMixinAdsTarget):

    def __init__(self, manager: SpKeyManager):
        self.manager = manager
        self._client = None

    @property
    def client(self):
        if not self._client:
            from core.apis.clients import ADS_FETCHER
            self._client = ADS_FETCHER.AMZ_ADS_FETCHER_IN.sp
        return self._client

    def read(self):
        df = self.client.list_keywords()
        df = self._transform_keywords_df(df)
        return df

    def sync(self):
        df = self.read()
        return self.manager.dfdb.sync(df)
