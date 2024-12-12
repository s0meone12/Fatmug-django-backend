from ....mixin import AmzAdsApiSubManagerMixinAdsTarget
from .main import SdNegTargetManager


class AmzAdsApiSubManagerSdNegTarget(AmzAdsApiSubManagerMixinAdsTarget):
    def __init__(self, manager: SdNegTargetManager):
        self.manager = manager
        self._client = None

    @property
    def client(self):
        if not self._client:
            from core.apis.clients import ADS_FETCHER
            self._client = ADS_FETCHER.AMZ_ADS_FETCHER_IN.sd
        return self._client

    def read(self):
        df = self.client.list_negative_targets()
        df = self._transform_targets_df(df)
        return df

    def sync(self):
        df = self.read()
        return self.manager.dfdb.sync(df)
