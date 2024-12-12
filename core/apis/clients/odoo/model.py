import pandas as pd
from tenacity import retry, stop_after_attempt, wait_fixed
from kn_api.odoo_api.odoo_operations import OddoModelOperation as OdooClient


class OdooModelClient:
    def __init__(self, model, fields=[]):
        self.client = OdooClient()
        self.model = model
        self.fields = fields

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(60))
    def _read(self, fields):
        if not fields:
            fields = self.fields
        response = self.client.search_read_record(
            self.model, {"filters": [], "fields": fields})
        
        return pd.DataFrame(response['data']['data'])

    def _create(self, data):
        pass

    def _write(self, data):
        pass

    def _unlink(self, data):
        pass

    # Implement all functionality from the DFDB handler here.
