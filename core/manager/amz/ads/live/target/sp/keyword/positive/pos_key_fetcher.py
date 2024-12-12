from ....base import TargetAmzAdsBaseFetcher
from .........apis.clients.amz.ads.fetcher import AmzAdsSpFetcher


class SpKeyAmzAdsModelFetcher(TargetAmzAdsBaseFetcher):

    def __init__(self):
        self._client = None

    @property
    def client(self):
        from core.apis.clients import AMZ_ADS_FETCHER_IN
        if not self._client:
            self._client = AMZ_ADS_FETCHER_IN.sp
        return self._client

    def read(self):
        df = self.client.list_keywords()
        df = self._transform_keywords_df(df)
        return df
