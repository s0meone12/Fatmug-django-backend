from django.utils import timezone
import pandas as pd
import datetime
from ....... import BaseManager


class AmzSbDiscProCampManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__aso = None
        self.__amz_sku = None
        self.__publisher = None
        self.__video_asset_id = None

    @property
    def aso(self):
        if not self.__aso:
            from .aso import AdsAssociatorSubManagerAmzSbDiscProCamp
            self.__aso = AdsAssociatorSubManagerAmzSbDiscProCamp(self)
        return self.__aso

    @property
    def amz_sku(self):
        if not self.__amz_sku:
            from .amz_sku import AmzSkuSubManagerSbDiscProCamp
            self.__amz_sku = AmzSkuSubManagerSbDiscProCamp(self)
        return self.__amz_sku

    @property
    def publisher(self):
        if not self.__publisher:
            from core.apis.clients import ADS_PUBLISHER
            self.__publisher = ADS_PUBLISHER.AMZ_ADS_PUBLISHER_IN.sb
        return self.__publisher

    @property
    def video_asset_id(self):
        if not self.__video_asset_id:
            from core.apis.clients import ADS_PUBLISHER
            self.__video_asset_id = ADS_PUBLISHER.AMZ_ADS_PUBLISHER_IN.sb_video_assets
        return self.__video_asset_id

    def no_of_live_targets(self, qs):
        """
        This Queryset is of Campaign model
        Write Logic below
        """
        pass

    def associater(self):
        disc_camp = self.filter(campaign__isnull=True)
        if not disc_camp.exists():
            return
        df = pd.DataFrame.from_records(disc_camp.values())
        df['campaign'] = df.apply(
            lambda row: {'campaign_id_code': row['campaign_id_code']}, axis=1)
        if not df.empty:
            return self.dfdb.sync(df)

    def _create_campaigns(self, qs=None):
        if qs is None:
            qs = self.all()
        disc_camp_qs = qs.filter(
            campaign__isnull=True, campaign_id_code__isnull=True).values('id', 'name', 'budget')
        if not disc_camp_qs.exists():    # This makes Early Exit, avoid the overhead of looping through an empty queryset
            return
        df = pd.DataFrame.from_records(disc_camp_qs)
        df['budget'] = df['budget'].astype(float)
        # Adding constants using assign
        df_body = df.assign(budgetType='DAILY',
                            brandEntityId='ENTITY2IK3PMA3W6DN',
                            startDate=datetime.datetime.now().date().strftime('%Y-%m-%d'),
                            state='ENABLED')
        df_response = self.publisher.create_campaign(df_body)  # API Call
        df_response['created_at'] = timezone.now()
        # Convert NaN values in campaign_id_code to None
        df_response = df_response.astype(object).where(
            pd.notnull(df_response), None)
        # Sync the filtered DataFrame with the database
        self.dfdb.sync(df_response)

    def _create_adgroups(self, qs=None):
        if qs is None:
            qs = self.all()
        disc_camp_qs = qs.filter(campaign__isnull=False, campaign_id_code__isnull=False, adgroup_id_code__isnull=True
                                 ).exclude(campaign_id_code='None').values('id', 'name', 'campaign_id_code')
        if not disc_camp_qs.exists():    # This makes Early Exit, avoid the overhead of looping through an empty queryset
            return
        df = pd.DataFrame.from_records(disc_camp_qs).rename(
            columns={'campaign_id_code': 'campaignId'})
        # Convert campaignId column to integer type
        df['campaignId'] = df['campaignId'].astype(int)
        # Adding constants using assign
        df_body = df.assign(state='ENABLED')
        df_response = self.publisher.create_adgroup(df_body)  # API Call
        df_response['updated_at'] = timezone.now()
        df_response = df_response.astype(object).where(
            pd.notnull(df_response), None)
        # Sync DataFrame with database
        self.dfdb.sync(df_response)

    def _create_adproducts(self, qs=None):
        if qs is None:
            qs = self.all()
        disc_camp_qs = qs.filter(campaign__isnull=False,
                                 campaign_id_code__isnull=False,
                                 adgroup_id_code__isnull=False
                                 ).exclude(campaign_id_code='None'
                                           ).exclude(ad_group_id_code='None'
                                                     ).values('id', 'name', 'ad_group_id_code', 'amz_sku__asin', 'amz_sku__id')
        if not disc_camp_qs.exists():
            return
        df = pd.DataFrame.from_records(disc_camp_qs)
        result_list = []
        for index, row in df.iterrows():
            video_asset_id = self.video_asset_id.generate_video_asset_id(
                row['name'], row['amz_sku__id'])
            # Convert ad_group_id_code to int if not null
            adgroup_id = int(row['ad_group_id_code']) if pd.notnull(
                row['ad_group_id_code']) else None
            result_dict = {
                "id": row['id'],
                "name": row['name'],
                "state": "ENABLED",
                "adGroupId": adgroup_id,
                "creative": {
                    "asins": [row['amz_sku__asin']],
                    "consentToTranslate": False,
                    "videoAssetIds": [video_asset_id]
                }
            }
            result_list.append(result_dict)
        df_body = pd.DataFrame(result_list)
        df_response = self.publisher.sb_add_product(df_body)  # API Call
        # Sync DataFrame with database
        df_response['updated_at'] = timezone.now()
        df_response = df_response.astype(object).where(
            pd.notnull(df_response), None)
        # Sync DataFrame with database
        self.dfdb.sync(df_response)

    def publish_create(self):
        self._create_campaigns()
        self._create_adgroups()
        self._create_adproducts()

    def publish_delete(self, qs=None):
        if qs is None:
            qs = self.all()
        disc_camp_qs = qs.filter(campaign__isnull=False, campaign__amz_sku__isnull=True).values(
            'id', 'campaign_id_code')
        if not disc_camp_qs.exists():
            return
        df_body = pd.DataFrame.from_records(disc_camp_qs).rename(
            columns={'campaign_id_code': 'campaignId'})
        # Convert campaignId column to integer type
        df_body['campaignId'] = df_body['campaignId'].astype(int)
        # Call the API to delete the campaigns
        df_response = self.publisher.delete_campaign(df_body)
        df_response['deleted_at'] = timezone.now()
        # Filter rows where message is "Success"
        success_df = df_response[df_response['message'] == "Success"]
        # Return only id, deleted_at, and message columns if message is "Success"
        success_df = success_df[['id', 'deleted_at', 'message']]
        # Sync DataFrame with database
        self.dfdb.sync(success_df)
