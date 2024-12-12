from ..mixin import OdooApiSubManagerMixinSku
from .main import SkuManager


class OdooApiSubManagerSku(OdooApiSubManagerMixinSku):
    def __init__(self, manager: SkuManager, fields=["product_id"]):
        super().__init__(fields)
        self.manager = manager

    def read(self, fields=[]):
        df = self._read_sku(fields)
        df.rename(columns={"product_id": "name"}, inplace=True)
        return df

    def sync(self):
        df = self.read()
        return self.manager.dfdb.sync(df)
