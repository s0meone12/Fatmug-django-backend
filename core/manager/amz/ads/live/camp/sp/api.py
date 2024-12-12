from ..mixin import AmzAdsApiSubManagerMixinAdCamp
from .main import SpCampManager


class AmzAdsApiSubManagerSpCamp(AmzAdsApiSubManagerMixinAdCamp):
    def __init__(self, manager: SpCampManager):
        self.manager = manager
        self.__client = None

    @property
    def client(self):
        if not self.__client:
            from core.apis.clients import ADS_FETCHER
            self.__client = ADS_FETCHER.AMZ_ADS_FETCHER_IN.sp
        return self.__client

    def read(self):
        df = self.client.list_campaigns()
        df = self._transform_budget_col(df)
        df = self._transform_campaigns_df(df)
        return df

    def sync(self):
        df = self.read()
        return self.manager.dfdb.sync(df)
