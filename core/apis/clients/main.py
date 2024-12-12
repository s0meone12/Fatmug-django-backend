from .amz.sell.main import AmzSpApiFetcher
from core.apis.clients.amz.ads.fetcher.main import AmzAdsFetcher
from core.apis.clients.amz.ads.publisher.main import AmzAdsPublisher
from sp_api.base.marketplaces import Marketplaces


class AmzSpApiFetcherMain:
    def __init__(self):
        self.__AMZ_SPAPI_IN = None
        self.__AMZ_SPAPI_US = None

    @property
    def AMZ_SPAPI_IN(self):
        if self.__AMZ_SPAPI_IN is None:
            self.__AMZ_SPAPI_IN = AmzSpApiFetcher(Marketplaces.IN)
        return self.__AMZ_SPAPI_IN

    @property
    def AMZ_SPAPI_US(self):
        if self.__AMZ_SPAPI_US is None:
            self.__AMZ_SPAPI_US = AmzSpApiFetcher(Marketplaces.US)
        return self.__AMZ_SPAPI_US
    
class AmzAdsFetcherMain:
    def __init__(self):
        self.__AMZ_ADS_FETCHER_IN = None
        self.__AMZ_ADS_FETCHER_US = None

    @property
    def AMZ_ADS_FETCHER_IN(self):
        if self.__AMZ_ADS_FETCHER_IN is None:
            self.__AMZ_ADS_FETCHER_IN = AmzAdsFetcher(Marketplaces.IN)
        return self.__AMZ_ADS_FETCHER_IN

    @property
    def AMZ_ADS_FETCHER_US(self):
        if self.__AMZ_ADS_FETCHER_US is None:
            self.__AMZ_ADS_FETCHER_US = AmzAdsFetcher(Marketplaces.US)
        return self.__AMZ_ADS_FETCHER_US
    
class AmzAdsPublisherMain:
    def __init__(self):
        self.__AMZ_ADS_PUBLISHER_IN = None
        self.__AMZ_ADS_PUBLISHER_US = None

    @property
    def AMZ_ADS_PUBLISHER_IN(self):
        if self.__AMZ_ADS_PUBLISHER_IN is None:
            self.__AMZ_ADS_PUBLISHER_IN = AmzAdsPublisher(Marketplaces.IN)
        return self.__AMZ_ADS_PUBLISHER_IN

    @property
    def AMZ_ADS_PUBLISHER_US(self):
        if self.__AMZ_ADS_PUBLISHER_US is None:
            self.__AMZ_ADS_PUBLISHER_US = AmzAdsPublisher(Marketplaces.US)
        return self.__AMZ_ADS_PUBLISHER_US


# Usage
SP_FETCHER = AmzSpApiFetcherMain()
ADS_FETCHER = AmzAdsFetcherMain()
ADS_PUBLISHER = AmzAdsPublisherMain()
