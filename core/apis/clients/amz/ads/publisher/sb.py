from kn_api._kn_ad_api.sb import CampaignsV4, Keywords, Targets
from kn_api._kn_ad_api.sb.ad_groups_v4 import AdGroupsV4
from kn_api._kn_ad_api.sb.add_product import ProductAdsV4
import json
import pandas as pd
from sp_api.base import Marketplaces
from .base import AmzAdsBasePublisher


class AmzAdsSbPublisher(AmzAdsBasePublisher):

    def __init__(self, marketplace: Marketplaces,  *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sb_campaign_client = CampaignsV4(marketplace)
        self.sb_add_product_client = ProductAdsV4(marketplace)
        self.sb_adgroup_client = AdGroupsV4(marketplace)
        self.sb_keyword_client = Keywords(marketplace)
        self.sb_target_client = Targets(marketplace)
        self.sb_chunk_size = 10

    def delete_campaign(self, df):
        response_data_list = []
        chunk_size = self.sb_chunk_size
        client = self.sb_campaign_client
        # Extracts the entire column as an array
        campaign_ids = df['campaignId'].values
        # Extracts the id_to_body_map column as an array
        id_to_body_map = df['id'].values

        for i in range(0, len(campaign_ids), chunk_size):
            campaigns_chunk = campaign_ids[i:i + chunk_size]
            request_data = {"campaignIdFilter": {
                "include": campaigns_chunk}
            }
            response = client.delete_campaigns(body=request_data)
            response_data = response.payload

            for data in response_data["campaigns"]["success"]:
                campaign_id_code = data["campaignId"]
                index = data["index"]
                id = id_to_body_map[i + index]
                # print(f"campaign_id_code: {campaign_id_code} deleted succesfully, now it is visible as Archived")
                response_data_list.append(
                    {"campaign_id_code": campaign_id_code, "message": "Success", "id": id})

            for data in response_data["campaigns"]["error"]:
                campaign_id_code = data["campaignId"]
                index = data["index"]
                id = id_to_body_map[i + index]
                # print(f"campaign_id_code: {campaign_id_code} not deleted, error occured: {data['error']['errors']}")
                response_data_list.append(
                    {"campaign_id_code": campaign_id_code, "message": f"Error : {data['errors']}", "id": id})

        response_df = pd.DataFrame(response_data_list)
        return response_df

    def update_campaign(self, df: pd.DataFrame) -> pd.DataFrame:
        df = self._transform_camp_df(df)
        response_data_list = []
        chunk_size = self.sb_chunk_size
        client = self.sb_campaign_client
        # Extracts the id_to_body_map column as an array
        id_to_body_map = df['id'].values
        # Remove the 'id' column from the DataFrame
        df.drop(columns=["id"], inplace=True)

        # Convert the DataFrame to a list of dictionaries
        list_of_campaigns_body = df.to_dict(orient="records")

        for i in range(0, len(list_of_campaigns_body), chunk_size):
            campaigns_chunk = list_of_campaigns_body[i:i + chunk_size]
            request_data = {"campaigns": campaigns_chunk}
            response = client.edit_campaigns(body=request_data)
            response_data = response.payload

            for data in response_data["campaigns"]["success"]:
                # campaign_id_code= data["campaignId"]
                index = data["index"]
                id = id_to_body_map[i + index]
                response_data_list.append(
                    {"message": "Success", "action_id": id, "state": "published"})

            for data in response_data["campaigns"]["error"]:
                index = data["index"]
                id = id_to_body_map[i + index]
                response_data_list.append(
                    {"message": f"Error : {data['errors']}", "action_id": id, "state": "error"})
        response_df = pd.DataFrame(response_data_list)
        return response_df

    def create_campaign(self, df):
        response_data_list = []
        chunk_size = self.sb_chunk_size
        client = self.sb_campaign_client
        id_to_body_map = df['id'].values
        df.drop(columns=["id"], inplace=True)

        # Convert the DataFrame to a list of dictionaries
        list_of_campaigns_body = df.to_dict(orient="records")

        for i in range(0, len(list_of_campaigns_body), chunk_size):
            campaigns_chunk = list_of_campaigns_body[i:i + chunk_size]
            request_data = {"campaigns": campaigns_chunk}
            response = client.create_campaigns(body=request_data)
            response_data = response.payload

            for data in response_data["campaigns"]["success"]:
                campaign_id_code = data["campaignId"]
                index = data["index"]
                id = id_to_body_map[i + index]
                response_data_list.append(
                    {"campaign_id_code": campaign_id_code, "message": "Success", "id": id})

            for data in response_data["campaigns"]["error"]:
                campaign_id_code = data["campaignId"]
                index = data["index"]
                id = id_to_body_map[i + index]
                response_data_list.append(
                    {"campaign_id_code": campaign_id_code, "message": f"Error : {data['errors']}", "id": id})

            response_df = pd.DataFrame(response_data_list)
        return response_df

    def create_adgroup(self, df):
        response_data_list = []
        chunk_size = self.sb_chunk_size
        client = self.sb_adgroup_client
        id_to_body_map = df['id'].values
        df.drop(columns=["id"], inplace=True)

        # Convert the DataFrame to a list of dictionaries
        list_of_adgroup_body = df.to_dict(orient="records")

        for i in range(0, len(list_of_adgroup_body), chunk_size):
            adgroup_chunk = list_of_adgroup_body[i:i + chunk_size]
            request_data = {"adGroups": adgroup_chunk}
            response = client.create_ad_groups(body=request_data)
            response_data = response.payload

            for data in response_data["adGroups"]["success"]:
                ad_group_id_code = data["adGroupId"]
                index = data["index"]
                id = id_to_body_map[i + index]
                response_data_list.append(
                    {"ad_group_id_code": ad_group_id_code, "message": "Success", "id": id})

            for data in response_data["adGroups"]["error"]:
                ad_group_id_code = None
                index = data["index"]
                id = id_to_body_map[i + index]
                response_data_list.append(
                    {"ad_group_id_code": ad_group_id_code, "message": f"Error : {data['errors']}", "id": id})
        response_df = pd.DataFrame(response_data_list)
        return response_df

    def sb_add_product(self, df):
        response_data_list = []
        chunk_size = self.sb_chunk_size
        id_to_body_map = df['id'].values
        df.drop(columns=["id"], inplace=True)

        # Convert the DataFrame to a list of dictionaries
        list_of_ad_product_body = df.to_dict(orient="records")

        for i in range(0, len(list_of_ad_product_body), chunk_size):
            ad_product_chunk = list_of_ad_product_body[i:i + chunk_size]
            request_data = {"ads": ad_product_chunk}
            response = self.sb_add_product_client.create_video_ads(
                body=request_data)
            response_data = response.payload

            for data in response_data["ads"]["success"]:
                ad_id_code = data["adId"]
                index = data["index"]
                id = id_to_body_map[i + index]
                response_data_list.append({
                    "id": id,
                    # "name": name,
                    # "amz_sku_asin": asin,
                    "ad_id_code": ad_id_code,
                    # "ad_group_id_code": ad_group_id_code,
                    "message": "Success"
                })
            for data in response_data["ads"]["error"]:
                index = data["index"]
                id = id_to_body_map[i + index]
                response_data_list.append({
                    "ad_id_code": None,
                    # "amz_sku_asin": asin,
                    "id": id,
                    # "ad_group_id_code": ad_group_id_code,
                    "message": f"Error at adGroupId generation: {data['errors']}"
                })
        response_df = pd.DataFrame(response_data_list)
        return response_df

    def create_keyword(self, df):
        response_data_list = []
        chunk_size = self.sb_chunk_size*10  # 100
        client = self.sb_keyword_client
        id_to_body_map = df['id'].values
        df.drop(columns=["id"], inplace=True)

        # Convert the DataFrame to a list of dictionaries
        list_of_keyword_body = df.to_dict(orient="records")

        for i in range(0, len(list_of_keyword_body), chunk_size):
            keywords_chunk = list_of_keyword_body[i:i + chunk_size]
            body = json.dumps(keywords_chunk)
            response = client.create_keywords(body=body)
            response_data = response.payload

            for index, keyword_result in enumerate(response_data):
                id = id_to_body_map[i + index]
                if keyword_result['code'] == 'SUCCESS':
                    keyword_id_code = keyword_result['keywordId']
                    response_data_list.append(
                        {"keyword_id_code": keyword_id_code, "message": "Success", "id": id})
                else:
                    response_data_list.append(
                        {"keyword_id_code": None, "message": f"Error : {keyword_result['message']}", "id": id})
        response_df = pd.DataFrame(response_data_list)
        return response_df

    def update_keyword(self, df):
        df = self._transform_sb_key_df(df)
        response_data_list = []
        chunk_size = self.sb_chunk_size*10  # 100
        client = self.sb_keyword_client
        id_to_body_map = df['id'].values
        df.drop(columns=["id"], inplace=True)

        # Convert the DataFrame to a list of dictionaries
        list_of_keyword_body = df.to_dict(orient="records")

        for i in range(0, len(list_of_keyword_body), chunk_size):
            keywords_chunk = list_of_keyword_body[i:i + chunk_size]
            body = json.dumps(keywords_chunk)
            response = client.edit_keywords(body=body)
            response_data = response.payload

            for index, keyword_result in enumerate(response_data):
                id = id_to_body_map[i + index]
                if keyword_result['code'] == 'Success':
                    # keyword_id_code = keyword_result['keywordId']
                    response_data_list.append(
                        {"state": "published", "message": "Success", "id": id})
                else:
                    response_data_list.append(
                        {"state": "error", "message": f"Error : {keyword_result['message']}", "id": id})

        response_df = pd.DataFrame(response_data_list)
        return response_df

    def delete_keyword(self, df):
        response_data_list = []
        chunk_size = self.sb_chunk_size*10  # 100
        client = self.sb_keyword_client
        id_to_body_map = df['id'].values
        df.drop(columns=["id"], inplace=True)

        # Convert the DataFrame to a list of dictionaries
        list_of_keyword_body = df.to_dict(orient="records")

        for i in range(0, len(list_of_keyword_body), chunk_size):
            keywords_chunk = list_of_keyword_body[i:i + chunk_size]
            body = json.dumps(keywords_chunk)
            response = client.edit_keywords(body=body)
            response_data = response.payload

            for index, keyword_result in enumerate(response_data):
                id = id_to_body_map[i + index]
                if keyword_result['code'] == 'Success':
                    keyword_id_code = keyword_result['keywordId']
                    response_data_list.append(
                        {"keyword_id_code": keyword_id_code, "message": "Success", "action_id": id})
                else:
                    response_data_list.append(
                        {"keyword_id_code": None, "message": f"Error : {keyword_result['message']}", "action_id": id})

        response_df = pd.DataFrame(response_data_list)
        return response_df

    def create_product_target_asin(self, df):
        response_data_list = []
        chunk_size = self.sb_chunk_size
        client = self.sb_target_client
        id_to_body_map = df['id'].values
        df.drop(columns=["id"], inplace=True)

        # Convert the DataFrame to a list of dictionaries
        list_of_target_body = df.to_dict(orient="records")

        for i in range(0, len(list_of_target_body), chunk_size):
            target_chunk = list_of_target_body[i:i + chunk_size]
            request_body = {"targets": target_chunk}
            body = json.dumps(request_body)
            response = client.create_products_targets(body=body)
            response_data = response.payload

            for data in response_data["createTargetSuccessResults"]:
                target_id_code = data["targetId"]
                index = data["targetRequestIndex"]
                id = id_to_body_map[i + index]
                response_data_list.append(
                    {"target_id_code": target_id_code, "message": "Success", "id": id})

            for data in response_data["createTargetErrorResults"]:
                target_id_code = None
                index = data["targetRequestIndex"]
                id = id_to_body_map[i + index]
                response_data_list.append(
                    {"target_id_code": target_id_code, "message": f"Error : {data['errors']}", "id": id})
        response_df = pd.DataFrame(response_data_list)
        return response_df

    def update_product_target_asin(self, df):
        df = self._transform_sb_pro_df(df)
        response_data_list = []
        chunk_size = self.sb_chunk_size
        client = self.sb_target_client
        id_to_body_map = df['id'].values
        df.drop(columns=["id"], inplace=True)

        # Convert the DataFrame to a list of dictionaries
        list_of_target_body = df.to_dict(orient="records")

        for i in range(0, len(list_of_target_body), chunk_size):
            target_chunk = list_of_target_body[i:i + chunk_size]
            request_body = {"targets": target_chunk}
            body = json.dumps(request_body)
            response = client.edit_products_targets(body=body)
            response_data = response.payload

            for data in response_data["updateTargetSuccessResults"]:
                # target_id_code= data["targetId"]
                index = data["targetRequestIndex"]
                id = id_to_body_map[i + index]
                response_data_list.append(
                    {"state": "published", "message": "Success", "action_id": id})

            for data in response_data["updateTargetErrorResults"]:
                index = data["targetRequestIndex"]
                id = id_to_body_map[i + index]
                # target_id_code= df.loc[i + index, "targetId"]
                response_data_list.append(
                    {"state": "error", "message": f"Error : {data['errors']}", "action_id": id})
        response_df = pd.DataFrame(response_data_list)
        return response_df

    def delete_product_target_asin(self, df):
        response_data_list = []
        chunk_size = self.sb_chunk_size
        client = self.sb_target_client
        id_to_body_map = df['id'].values
        df.drop(columns=["id"], inplace=True)

        # Convert the DataFrame to a list of dictionaries
        list_of_target_body = df.to_dict(orient="records")

        for i in range(0, len(list_of_target_body), chunk_size):
            target_chunk = list_of_target_body[i:i + chunk_size]
            request_body = {"targets": target_chunk}
            body = json.dumps(request_body)
            response = client.edit_products_targets(body=body)
            response_data = response.payload

            for data in response_data["updateTargetSuccessResults"]:
                target_id_code = data["targetId"]
                index = data["targetRequestIndex"]
                id = id_to_body_map[i + index]
                response_data_list.append(
                    {"target_id_code": target_id_code, "message": "Success", "action_id": id})

            for data in response_data["updateTargetErrorResults"]:
                index = data["targetRequestIndex"]
                id = id_to_body_map[i + index]
                # target_id_code= df.loc[i + index, "targetId"]
                target_id_code = None
                response_data_list.append(
                    {"target_id_code": target_id_code, "message": f"Error : {data['errors']}", "action_id": id})
        response_df = pd.DataFrame(response_data_list)
        return response_df
