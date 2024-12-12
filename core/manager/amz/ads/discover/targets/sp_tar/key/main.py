import pandas as pd
from django.apps import apps
from .......base import BaseManager
from django.db.models import Count
from django.utils import timezone


class SPDiscKeyTgtManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__amz_sku = None
        self.__camp = None
        self._sku_disc_key = None
        self._publisher = None

    @property
    def amz_sku(self):
        if not self.__amz_sku:
            from .amz_sku import AmzSkuSubManagerSPDiscKeyTgt
            self.__amz_sku = AmzSkuSubManagerSPDiscKeyTgt(self)
        return self.__amz_sku

    @property
    def sku_disc_tgt(self):
        if not self.__sku_disc_tgt:
            from .sku_disc import SkuDiscKeySubManagerSpDiscKeyTrgt
            self.__sku_disc_tgt = SkuDiscKeySubManagerSpDiscKeyTrgt(self)
        return self.__sku_disc_tgt

    @property
    def camp(self):
        if not self.__camp:
            from .disc_camp import SpKeyCampSubManagerTarget
            self.__camp = SpKeyCampSubManagerTarget(self)
        return self.__camp

    @property
    def publisher(self):
        if not self.__publisher:
            from core.apis.clients import ADS_PUBLISHER
            self.__publisher = ADS_PUBLISHER.AMZ_ADS_PUBLISHER_IN.sp
        return self.__publisher

    def fk_mapping_on_disc_trgt(self):
        data = []
        skus = self.values_list('sku_disc_tgt__sku_id', flat=True).distinct()
        # Loop over each SKU
        for sku in skus:
            discovered_keyword_targets = self.filter(keyword__isnull=True,
                                                     disc_campaign__isnull=True, sku_disc_tgt__sku=sku)
            # make a list of keywords that we discovered for this particular sku and we have to append this in our data
            list_of_key_to_populate = list(
                discovered_keyword_targets.values('id', 'target_name'))

            # fetch directly both camps and count of keyword in it
            campaigns_key_tgt_count_details = self.filter(
                disc_campaign__campaign__isnull=False,
                disc_campaign__campaign__amz_sku=sku
            ).values('disc_campaign').annotate(sku_disc_tgt_count=Count("sku_disc_tgt", distinct=True))

            for details in campaigns_key_tgt_count_details:
                campaign_name_id = details['disc_campaign']
                no_of_keywords_in_existing_camp = details['sku_disc_tgt_count']
                empty_space = 1000 - no_of_keywords_in_existing_camp

                while empty_space > 0 and len(list_of_key_to_populate) > 0:
                    # pop out last discovered keyword id and store in the data list
                    temp = list_of_key_to_populate.pop()
                    sku_disc_tgt_id = temp['id']
                    target_name = temp['target_name']
                    # Append data to lists
                    data.append({'sku_disc_tgt': sku_disc_tgt_id,
                                'disc_campaign': campaign_name_id, 'bid': 0, "target_name": target_name})
                    empty_space -= 1

                if len(list_of_key_to_populate) == 0:
                    break

            # if there are still discoverd keywords left after filling the existing camp
            # now we strt filling in new camp
            if len(list_of_key_to_populate) != 0:
                # new camp have empty campaign field
                new_camp = self.camp.model.objects.filter(
                    campaign__isnull=True, amz_sku=sku)
                for camp in new_camp:
                    empty_space = 1000

                    while empty_space > 0 and len(list_of_key_to_populate) > 0:
                        # pop out last discovered keyword and store in the list
                        temp = list_of_key_to_populate.pop()
                        sku_disc_tgt_id = temp['id']
                        target_name = temp['target_name'].upper()
                        # Append data to lists
                        data.append({'sku_disc_tgt': sku_disc_tgt_id,
                                    'disc_campaign': camp.id, 'bid': 0, "target_name": target_name})
                        empty_space -= 1

                    if len(list_of_key_to_populate) == 0:
                        break
                    else:
                        ValueError(
                            "there is no space in the camp, plz add new camp")
        if data:
            sync_df = pd.DataFrame(data)
            return self.dfdb.sync(sync_df)

    def associater(self):
        disc_targ = self.filter(keyword_id_code__isnull=True)
        if not disc_targ.exists():
            return
        df = pd.DataFrame.from_records(disc_targ.values())
        df['keyword'] = df.apply(
            lambda row: {'keyword_id_code': row['keyword_id_code']}, axis=1)
        if not df.empty:
            return self.dfdb.sync(df)

    def update_spend_matrix(self):
        """
        This method will update the spend matrix, i.e lifetime_spend and spend_since_mute fields for the targets model
        """
        from core.models import AmzAdsSpTgtRpt

        # Fetch all targets at once
        targets_df = pd.DataFrame(
            list(self.filter(keyword__isnull=False).values()))
        # Fetch all spend data at once
        spend_data_df = pd.DataFrame(
            list(AmzAdsSpTgtRpt.objects.filter(keyword__isnull=False).values()))

        # Initialize an empty list to store the results
        results = []
        # Iterate over the targets
        for _, target in targets_df.iterrows():
            # Filter the spend data for the current target
            target_spend_data = spend_data_df[spend_data_df['keyword_id']
                                              == target['keyword_id']]

            # Calculate lifetime_spend and spend_since_mute
            lifetime_spend = target_spend_data['cost'].sum()
            spend_since_mute = target_spend_data[target_spend_data['date'] >=
                                                 target['muted_on']]['cost'].sum() if target['muted_on'] else 0

            results.append({
                'id': target['id'],
                'lifetime_spend': lifetime_spend,
                'spend_since_mute': spend_since_mute
            })
        df = pd.DataFrame(results)
        print(df)
        return self.dfdb.sync(df)

    def publish_create(self, qs=None):
        if qs is None:
            qs = self.all()
        disc_key_qs = qs.filter(keyword__isnull=True, keyword_id_code__isnull=True,
                                disc_campain__campaign_id_code__isnull=False,
                                disc_campaign__adgroup_id_code__isnull=False
                                ).values('id', 'disc_campaign__campaign_id_code', 'disc_campaign__adgroup_id_code', 'sku_disc_key__name', 'bid')
        if not disc_key_qs.exists():    # This makes Early Exit, avoid the overhead of looping through an empty queryset
            return
        df = pd.DataFrame.from_records(disc_key_qs)
        result_list = []
        for index, row in df.iterrows():
            # Convert ad_group_id_code and campaign_id_code to int
            campaign_id = int(row['disc_campaign__campaign_id_code'])
            adgroup_id = int(row['disc_campaign__adgroup_id_code'])
            result_dict = {
                "id": row['id'],
                "bid": row['bid'],
                "adGroupId": adgroup_id,
                "campaignId": campaign_id,
                "matchType": "exact",
                "keywordText": row["sku_disc_tgt__name"]
            }
            result_list.append(result_dict)
        df_body = pd.DataFrame(result_list)
        df_response = self.publisher.create_keyword(df_body)  # API Call
        df_response['created_at'] = timezone.now()
        # Convert NaN values in keyword_id_code to None
        df_response = df_response.astype(object).where(
            pd.notnull(df_response), None)
       # Sync the DataFrame with the database
        self.dfdb.sync(df_response)
