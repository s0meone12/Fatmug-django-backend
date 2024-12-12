import pandas as pd
from rest_framework import status
from kn_api.odoo_api.odoo_operations import OddoModelOperation as OdooClient
import json


class OdooVideoCompressionClient:
    def __init__(self):
        self.client = OdooClient()

    def write_model(self, id, model_name, new_file_url, field_url, field_bool):
        data1 = {"records": [{"id": id, f'{field_url}': new_file_url}]}
        res = self.client.update_record(model_name, data1)
        if res['staus'] == status.HTTP_200_OK:
            data2 = {"records": [{"id": id, f'{field_bool}': True}]}
            ress = self.client.update_record(model_name, data2)
            if ress['staus'] == status.HTTP_200_OK:
                return True
            return False
        return False

    def read_uncompress_video_url(self):
        response = self.client.get_list_of_uncompress_file()
        data = response['data']
        li = json.loads(data['result'])
        df = pd.DataFrame(li)
        return df
