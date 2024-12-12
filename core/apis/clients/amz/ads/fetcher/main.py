from sp_api.base.marketplaces import Marketplaces


class AmzAdsFetcher:
    """
    Main Fetcher for Sponsored Brands, Sponsored Display and Sponsored Products.
    """

    def __init__(self, marketplace: Marketplaces, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._marketplace = marketplace
        print(f"Initalizing AmzAdsApiFetcher for {marketplace}")
        self.__sb = None
        self.__sd = None
        self.__sp = None

    @property
    def sb(self):
        if not self.__sb:
            from .sb import AmzAdsSbFetcher
            self.__sb = AmzAdsSbFetcher(self._marketplace)
        return self.__sb

    @property
    def sd(self):
        if not self.__sd:
            from .sd import AmzAdsSdFetcher
            self.__sd = AmzAdsSdFetcher(self._marketplace)
        return self.__sd

    @property
    def sp(self):
        if not self.__sp:
            from .sp import AmzAdsSpFetcher
            self.__sp = AmzAdsSpFetcher(self._marketplace)
        return self.__sp
