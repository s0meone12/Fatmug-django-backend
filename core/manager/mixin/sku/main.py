from core.apis.clients.odoo import OdooModelClient


class OdooApiSubManagerMixinSku:
    def __init__(self, fields):
        self.client = OdooModelClient('kn.amz.sku', fields)
        self.model = 'kn.amz.sku'
        self.fields = fields

    def _read_amz_sku(self, fields):
        df = self.client._read(fields)
        df['product_id'] = df['product_id'].apply(
            lambda x: x[1] if x else None)
        df.drop(columns=['id'], inplace=True)
        return df

    def _read_sku(self, fields):
        df = self._read_amz_sku(fields)
        df = df[df['product_id'].notnull()]
        return df
