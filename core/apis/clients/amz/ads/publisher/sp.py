from kn_api._kn_ad_api.sp import CampaignsV3, AdGroupsV3, KeywordsV3, TargetsV3
from kn_api._kn_ad_api.sp.add_product import ProductAdsV3
import json, pandas as pd
from sp_api.base import Marketplaces
from .base import AmzAdsBasePublisher


class AmzAdsSpPublisher(AmzAdsBasePublisher):
    """
    Sponsored Products Publisher
    """
    def __init__(self, marketplace: Marketplaces,  *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sp_campaign_client = CampaignsV3(Marketplaces.IN)
        self.sp_add_product_client = ProductAdsV3(Marketplaces.IN)
        self.sp_adgroup_client = AdGroupsV3(Marketplaces.IN)
        self.sp_keyword_client = KeywordsV3(Marketplaces.IN)
        self.sp_target_client = TargetsV3(Marketplaces.IN)
        self.sp_chunk_size=1000
        
    def delete_campaign(self, df):
        response_data_list=[]
        chunk_size = self.sp_chunk_size
        client = self.sp_campaign_client
        campaign_ids = df['campaignId'].values  # Extracts the entire column as an array
        id_to_body_map = df['id'].values  # Extracts the id_to_body_map column as an array
        
        for i in range(0, len(campaign_ids), chunk_size):
            campaigns_chunk = campaign_ids[i:i + chunk_size]
            id_chunk = id_to_body_map[i:i + chunk_size]  # Extract the corresponding chunk of ids
            request_data = {"campaignIdFilter": {
                                "include": campaigns_chunk}
                            }
            response = client.delete_campaigns(body=request_data)
            response_data = response.payload

            for data in response_data["campaigns"]["success"]:
                campaign_id_code= data["campaignId"]
                index = data["index"]
                id = id_to_body_map[i + index]
                # print(f"campaign_id_code: {campaign_id_code} deleted succesfully, now it is visible as Archived")
                response_data_list.append({"campaign_id_code": campaign_id_code, "message": "Success", "id": id})

            for data in response_data["campaigns"]["error"]:
                campaign_id_code= data["campaignId"]
                index = data["index"]
                id = id_to_body_map[i + index]
                # print(f"campaign_id_code: {campaign_id_code} not deleted, error occured: {data['error']['errors']}")
                response_data_list.append({"campaign_id_code": campaign_id_code, "message": f"Error : {data['errors']}", "id": id})
        return response_data_list
    
    def update_campaign(self, df):
        df = self._transform_camp_df(df)
        df["targetingType"] = "MANUAL"
        df["budgetType"] = "DAILY"
        response_data_list=[]
        chunk_size = self.sp_chunk_size
        client = self.sp_campaign_client
        id_to_body_map = df['id'].values  # Extracts the id_to_body_map column as an array
        df.drop(columns=["id"], inplace=True)  # Remove the 'id' column from the DataFrame

        # Convert the DataFrame to a list of dictionaries
        list_of_campaigns_body = df.to_dict(orient="records")
        # Adjust each dictionary to include the nested 'budget' structure
        for record in list_of_campaigns_body:
            budget_details = {
                "budgetType": record.pop("budgetType"),  # Remove and return 'budgetType'
                "budget": record.pop("budget")  # Remove and return 'budget'
            }
            record["budget"] = budget_details  # Add the nested 'budget' dictionary
        
        for i in range(0, len(list_of_campaigns_body), chunk_size):
            campaigns_chunk = list_of_campaigns_body[i:i + chunk_size]
            request_data = {"campaigns": campaigns_chunk}
            response = client.edit_campaigns(body=request_data)
            response_data = response.payload

            for data in response_data["campaigns"]["success"]:
                # campaign_id_code= data["campaignId"]
                index = data["index"]
                id = id_to_body_map[i + index]
                response_data_list.append({"id": id, "message": "Success", "state": "published"})

            for data in response_data["campaigns"]["error"]:
                index = data["index"]
                id = id_to_body_map[i + index]
                response_data_list.append({ "id": id, "message": f"Error : {data['errors']}", "state": "error"})
        response_df = pd.DataFrame(response_data_list)
        return response_df

    def create_campaign(self, df):
        response_data_list=[]
        chunk_size = self.sp_chunk_size
        client = self.sp_campaign_client
        id_to_body_map = df['id'].values
        df.drop(columns=["id"], inplace=True)

        # Convert the DataFrame to a list of dictionaries
        list_of_campaigns_body = df.to_dict(orient="records")
        # Adjust each dictionary to include the nested 'budget' structure
        for record in list_of_campaigns_body:
            budget_details = {
                "budgetType": record.pop("budgetType"),  # Remove and return 'budgetType'
                "budget": record.pop("budget")  # Remove and return 'budget'
            }
            record["budget"] = budget_details


        for i in range(0, len(list_of_campaigns_body), chunk_size):
            campaigns_chunk = list_of_campaigns_body[i:i + chunk_size]
            request_data = {"campaigns": campaigns_chunk}
            response = client.create_campaigns(body=request_data)
            response_data = response.payload

            for data in response_data["campaigns"]["success"]:
                campaign_id_code= data["campaignId"]
                index = data["index"]
                id = id_to_body_map[i + index]
                response_data_list.append({"campaign_id_code": campaign_id_code, "message": "Success", "id": id})

            for data in response_data["campaigns"]["error"]:
                campaign_id_code= data["campaignId"]
                index = data["index"]
                id = id_to_body_map[i + index]
                response_data_list.append({"campaign_id_code": campaign_id_code, "message": f"Error : {data['errors']}", "id": id})
            
            response_df = pd.DataFrame(response_data_list)
        return response_df

    def create_adgroup(self, df):
        response_data_list=[]
        chunk_size = self.sp_chunk_size
        client = self.sp_adgroup_client
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
                ad_group_id_code= data["adGroupId"]
                index = data["index"]
                id = id_to_body_map[i + index]
                response_data_list.append({"ad_group_id_code": ad_group_id_code, "message": "Success", "id": id})
            
            for data in response_data["adGroups"]["error"]:
                ad_group_id_code= None
                index = data["index"]
                id = id_to_body_map[i + index]
                response_data_list.append({"ad_group_id_code": ad_group_id_code, "message": f"Error : {data['errors']}", "id": id})
        response_df = pd.DataFrame(response_data_list)
        return response_df
    
    def sp_add_product(self, df):
        response_data_list = []
        chunk_size = self.sp_chunk_size
        client = self.sp_add_product_client
        id_to_body_map = df['id'].values
        df.drop(columns=["id"], inplace=True)

        # Convert the DataFrame to a list of dictionaries
        list_of_products_body = df.to_dict(orient="records")
        
        for i in range(0, len(list_of_products_body), chunk_size):
            ad_product_chunk = list_of_products_body[i:i + chunk_size]
            request_data = {"productAds": ad_product_chunk}
            response = client.create_product_ads(body=request_data)
            response_data = response.payload

            for data in response_data["productAds"]["success"]:
                ad_product_id_code= data["adId"]
                index = data["index"]
                id = id_to_body_map[i + index]
                response_data_list.append({"ad_product_id_code": ad_product_id_code, "message": "Success", "id": id})

            for data in response_data["productAds"]["error"]:
                ad_product_id_code= None
                index = data["index"]
                id = id_to_body_map[i + index]
                response_data_list.append({"ad_product_id_code": ad_product_id_code, "message": f"Error : {data['errors']}", "id": id})

        response_df = pd.DataFrame(response_data_list)
        return response_df

    def create_keyword(self, df):
        response_data_list = []
        chunk_size = self.sp_chunk_size
        client = self.sp_keyword_client
        id_to_body_map = df['id'].values
        df.drop(columns=["id"], inplace=True)

        # Convert the DataFrame to a list of dictionaries
        list_of_keywords_body = df.to_dict(orient="records")
        
        for i in range(0, len(list_of_keywords_body), chunk_size):
            keyword_chunk = list_of_keywords_body[i:i + chunk_size]
            request_data = {"keywords": keyword_chunk}
            response = client.create_keyword(body=request_data)
            response_data = response.payload

            for data in response_data["keywords"]["success"]:
                keyword_id_code= data["keywordId"]
                index = data["index"]
                id = id_to_body_map[i + index]
                response_data_list.append({"keyword_id_code": keyword_id_code, "message": "Success", "id": id})

            for data in response_data["keywords"]["error"]:
                keyword_id_code= None
                index = data["index"]
                id = id_to_body_map[i + index]
                response_data_list.append({"keyword_id_code": keyword_id_code, "message": f"Error : {data['errors']}", "id": id})

        response_df = pd.DataFrame(response_data_list)
        return response_df
    
    def update_keyword(self, df):
        df = self._transform_sp_key_df(df)
        response_data_list = []
        chunk_size = self.sp_chunk_size
        client = self.sp_keyword_client
        id_to_body_map = df['id'].values
        df.drop(columns=["id"], inplace=True)

        # Convert the DataFrame to a list of dictionaries
        list_of_keywords_body = df.to_dict(orient="records")
        
        for i in range(0, len(list_of_keywords_body), chunk_size):
            keyword_chunk = list_of_keywords_body[i:i + chunk_size]
            request_data = {"keywords": keyword_chunk}
            response = client.edit_keyword(body=request_data)
            response_data = response.payload

            for data in response_data["keywords"]["success"]:
                # keyword_id_code= data["keywordId"]
                index = data["index"]
                id = id_to_body_map[i + index]
                response_data_list.append({"state": "published", "message": "Success", "id": id})

            for data in response_data["keywords"]["error"]:
                index = data["index"]
                id = id_to_body_map[i + index]
                # keyword_id_code = df.loc[i+index, 'keywordId']
                response_data_list.append({"state": "error", "message": f"Error : {data['errors']}", "id": id})

        response_df = pd.DataFrame(response_data_list)
        return response_df
    
    def delete_keyword(self, df):
        response_data_list = []
        chunk_size = self.sp_chunk_size
        client = self.sp_keyword_client
        keyword_ids = df['keywordId'].values
        id_to_body_map = df['id'].values

        for i in range(0, len(keyword_ids), chunk_size):
            keyword_chunk = keyword_ids[i:i + chunk_size]
            id_chunk = id_to_body_map[i:i + chunk_size]
            request_data = {"keywordIdFilter": {"include": keyword_chunk}}
            response = client.delete_keywords(body=request_data)
            response_data = response.payload

            for data in response_data["keywords"]["success"]:
                keyword_id_code= data["keywordId"]
                index = data["index"]
                id = id_to_body_map[i + index]
                response_data_list.append({"keyword_id_code": keyword_id_code, "message": "Success", "action_id": id})

            for data in response_data["keywords"]["error"]:
                index = data["index"]
                id = id_to_body_map[i + index]
                # keyword_id_code = df.loc[i+index, 'keywordId']
                keyword_id_code= None
                response_data_list.append({"keyword_id_code": keyword_id_code, "message": f"Error : {data['errors']}", "action_id": id})

        response_df = pd.DataFrame(response_data_list)
        return response_df
    
    def create_product_targeting_asin(self, df):
        response_data_list = []
        chunk_size = self.sp_chunk_size
        client = self.sp_target_client
        id_to_body_map = df['id'].values
        df.drop(columns=["id"], inplace=True)

        # Convert the DataFrame to a list of dictionaries
        list_of_pro_trgt_body = df.to_dict(orient="records")
        
        for i in range(0, len(list_of_pro_trgt_body), chunk_size):
            product_targeting_chunk = list_of_pro_trgt_body[i:i + chunk_size]
            request_data = {"targetingClauses": product_targeting_chunk}
            response = client.create_product_targets(body=request_data)
            response_data = response.payload

            for data in response_data["targetingClauses"]["success"]:
                target_id_code= data["targetId"]
                index = data["index"]
                id = id_to_body_map[i + index]
                response_data_list.append({"target_id_code": target_id_code, "message": "Success", "id": id})

            for data in response_data["targeting"]["error"]:
                target_id_code= None
                index = data["index"]
                id = id_to_body_map[i + index]
                response_data_list.append({"target_id_code": target_id_code, "message": f"Error : {data['errors']}", "id": id})

        response_df = pd.DataFrame(response_data_list)
        return response_df
    
    def update_product_targeting_asin(self, df):
        df = self._transform_sp_pro_df(df)
        response_data_list = []
        chunk_size = self.sp_chunk_size
        client = self.sp_target_client
        id_to_body_map = df['id'].values
        df.drop(columns=["id"], inplace=True)

        # Convert the DataFrame to a list of dictionaries
        list_of_pro_trgt_body = df.to_dict(orient="records")
        
        for i in range(0, len(list_of_pro_trgt_body), chunk_size):
            product_targeting_chunk = list_of_pro_trgt_body[i:i + chunk_size]
            request_data = {"targetingClauses": product_targeting_chunk}
            response = client.edit_product_targets(body=request_data)
            response_data = response.payload

            for data in response_data["targetingClauses"]["success"]:
                # targeting_id_code= data["targetId"]
                index = data["index"]
                id = id_to_body_map[i + index]
                response_data_list.append({"state": "published", "message": "Success", "action_id": id})

            for data in response_data["targeting"]["error"]:
                index = data["index"]
                id = id_to_body_map[i + index]
                # targeting_id_code = df.loc[i+index, 'targetId']
                targeting_id_code= None
                response_data_list.append({"state": "error", "message": f"Error : {data['errors']}", "action_id": id})

        response_df = pd.DataFrame(response_data_list)
        return response_df
    
    def delete_product_targeting_asin(self, df):
        response_data_list = []
        chunk_size = self.sp_chunk_size
        client = self.sp_target_client
        target_ids = df['targetId'].values
        id_to_body_map = df['id'].values

        for i in range(0, len(target_ids), chunk_size):
            target_chunk = target_ids[i:i + chunk_size]
            request_data = {"targetIdFilter": {"include": target_chunk}}
            response = client.delete_product_targets(body=request_data)
            response_data = response.payload

            for data in response_data["targetingClauses"]["success"]:
                target_id_code= data["targetId"]
                index = data["index"]
                id = id_to_body_map[i + index]
                response_data_list.append({"target_id_code": target_id_code, "message": "Success", "action_id": id})

            for data in response_data["targeting"]["error"]:
                index = data["index"]
                id = id_to_body_map[i + index]
                # targeting_id_code = df.loc[i+index, 'targetId']
                target_id_code= None
                response_data_list.append({"target_id_code": target_id_code, "message": f"Error : {data['errors']}", "action_id": id})

        response_df = pd.DataFrame(response_data_list)
        return response_df