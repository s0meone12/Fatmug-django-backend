from sp_api.base.marketplaces import Marketplaces
from .sku import AmzSkuFetcher

class AmzSpApiListingFetcher:
    def __init__(self, marketplace: Marketplaces, *args, **kwargs):
        self.sku = AmzSkuFetcher(marketplace)
