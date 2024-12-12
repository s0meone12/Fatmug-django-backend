import pandas as pd
from rest_framework import status
from kn_api.odoo_api.odoo_operations import OddoModelOperation
import json


class OdooFetcher:
    def __init__(self):
        self.obj = OddoModelOperation()

    def write_model(self, model_name, data):
        data1 = {"records": [data]}
        res = self.obj.update_record(model_name, data1)
        print("-X>", res)
        return True if res["status"] == status.HTTP_200_OK else False

    def read_model(self, model_name, fields=[], filters=[]):
        data = {"filters": filters, "fields": fields}
        search_record_resp = self.obj.search_read_record(model_name, data)
        print(search_record_resp)
        df = pd.DataFrame(search_record_resp["data"]["data"])
        return df

    def read_amz_skus(
        self,
        fields=[
            "product_id",
            "sku_code",
            "asin",
            "is_discontinued",
            "fba_inv_days",
            "str_qc_re_rts_trns_fba_inv_days",
            "sale_price",
            "desired_ads_percentage",
        ],
    ):
        return self.read_model("kn.amz.sku", fields)

    def read_uncompress_video_url(self):
        response = self.obj.get_list_of_uncompress_file()
        data = response["data"]
        li = json.loads(data["result"])
        df = pd.DataFrame(li)
        return df
