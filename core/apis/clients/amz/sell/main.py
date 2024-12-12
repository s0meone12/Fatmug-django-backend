from .reports.main import AmzSpApiReportFetcher
from sp_api.base.marketplaces import Marketplaces
from .listing.main import AmzSpApiListingFetcher

class AmzSpApiFetcher:
    def __init__(self, marketplace: Marketplaces, *args, **kwargs):
        print(f"Initalizing AmzSpApiFetcher for {marketplace}")
        self._marketplace = marketplace
        self._reports = None
        self._listing = None

    @property
    def reports(self):
        if not self._reports:
            self._reports = AmzSpApiReportFetcher(self._marketplace)
        return self._reports
    
    @property
    def listing(self):
        if not self._listing:
            self._listing = AmzSpApiListingFetcher(self._marketplace)
        return self._listing