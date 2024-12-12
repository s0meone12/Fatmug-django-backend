import pandas as pd
from core.apis.clients import SP_FETCHER
import asyncio
from .main import AmzSkuManager


class SpApiSubManagerAmzSku:

    def __init__(self, manager: AmzSkuManager):
        self.manager = manager
        self.__listing = SP_FETCHER.AMZ_SPAPI_IN.listing.sku

    def _read_sale_price(self) -> pd.DataFrame:
        return self.__listing.get_sale_price()

    def sync_sale_price(self):
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            print("Creating new event loop")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        df = loop.run_until_complete(self._read_sale_price())
        if not df is None:
            self.manager.dfdb.sync(df=df)

    def _read_product_type(self) -> pd.DataFrame:
        return self.__listing.get_product_type()

    def sync_product_type(self):
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            print("Creating new event loop")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        df = loop.run_until_complete(self._read_product_type())
        if not df is None:
            self.manager.dfdb.sync(df=df)
