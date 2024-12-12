from kn_api._kn_sp_api.listings_items import ListingsItems
from sp_api.base.marketplaces import Marketplaces


class AmzSpApiListingBaseFetcher:
    def __init__(self, marketplace: Marketplaces, *args, **kwargs):
        self.marketplace = marketplace
        self.client: ListingsItems = ListingsItems(marketplace=marketplace)
