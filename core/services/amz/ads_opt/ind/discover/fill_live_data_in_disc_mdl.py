from core.models import *
import pandas as pd
import ast


class AddLiveDataInDiscModels():
    """
    This class will sync all the 10 discover models, with live data. [4 camp models(SBDiscKeyCamp, SBDiscProCamp, SPDiscKeyCamp, SPDiscProCamp)],
    [2 sku discovered targets(AmzSkuDiscKey, AmzSkuDiscProTgt)] and [4 discovered camp targets(
    SPDiscKeyTgt, SPDiscProTgt, SBDiscKeyTgt, SBDiscProTgt)]
    """

    def get_disc_sp_sb_camp_df(self, keywords_data, targets_data, campaign_type):

        if campaign_type == "sp":
            amz_ads_camp_type = AmzSpAdsCamp
            amz_ads_key_type = AmzSpAdsKeyword
            amz_ads_tgt_type = AmzSpAdsTarget
            asin_category = 'asin_same_as'
            live_campaigns = amz_ads_camp_type.objects.filter(state='enabled').exclude(
                targeting_type='auto').exclude(name__icontains='fetch')
        else:
            amz_ads_camp_type = AmzSbAdsCamp
            amz_ads_key_type = AmzSbAdsKeyword
            amz_ads_tgt_type = AmzSbAdsTarget
            asin_category = 'asinsameas'
            live_campaigns = amz_ads_camp_type.objects.filter(
                state='enabled').exclude(name__icontains='fetch')

        sp_sb_camp_key_data = []
        sp_sb_camp_pro_data = []

        # for SP/SB, manual camp, whose sku is not null

        for campaign in live_campaigns:
            # Check if keywords exist for the campaign
            camp_keywords = amz_ads_key_type.objects.filter(
                campaign__campaign_id_code=campaign.campaign_id_code)
            if camp_keywords:
                ad_group_ids = camp_keywords.values(
                    'ad_group_id_code').distinct()
                if len(ad_group_ids) > 1:
                    raise ValueError("More than one ad_group_id_code found.")
                elif len(ad_group_ids) == 1:
                    ad_group_id = ad_group_ids[0]['ad_group_id_code']
                else:
                    raise ValueError("No ad_group_id_code found.")

                # Create SPDiscProCamp/SBDiscProCamp object if keywords exist
                sku_id = campaign.amz_sku.id if campaign.amz_sku else None
                sp_sb_camp_key_data.append({'campaign': campaign.id, 'name': campaign.name, 'budget': campaign.budget,
                                           'campaign_id_code': campaign.campaign_id_code, 'ad_group_id_code': ad_group_id, 'amz_sku': sku_id})
                if sku_id == None:
                    print(campaign.id, "sku is none")
                    continue
                # Create AmzSkuDiscKey objects for each keyword
                for keyword in camp_keywords:
                    keywords_data.append({'sku': keyword.campaign.amz_sku.id, 'name': keyword.keyword_text,
                                         'clicks': 0, 'impressions': 0, 'cost': 0, 'sales': 0})

            # Check if targets exist for the campaign
            camp_targets = amz_ads_tgt_type.objects.filter(
                campaign__campaign_id_code=campaign.campaign_id_code)
            if camp_targets:
                ad_group_ids = camp_targets.values(
                    'ad_group_id_code').distinct()
                if len(ad_group_ids) > 1:
                    raise ValueError("More than one ad_group_id_code found.")
                elif len(ad_group_ids) == 1:
                    ad_group_id = ad_group_ids[0]['ad_group_id_code']
                else:
                    raise ValueError("No ad_group_id_code found.")

                # Create SPDiscProCamp/SBDiscProCamp object if targets exist
                sku_id = campaign.amz_sku.id if campaign.amz_sku else None
                sp_sb_camp_pro_data.append({'campaign': campaign.id, 'name': campaign.name, 'budget': campaign.budget,
                                           'campaign_id_code': campaign.campaign_id_code, 'ad_group_id_code': ad_group_id, 'amz_sku': sku_id})
                if sku_id == None:
                    print(campaign.id, "sku is none")
                    continue
                # Create AmzSkuDiscProTgt objects for each target
                for target in camp_targets:
                    exp = ast.literal_eval(target.expression)
                    # print(exp)
                    if 'value' in exp[0] and exp[0]['type'].lower() == asin_category:
                        asin = exp[0]['value']
                        targets_data.append({'sku': target.campaign.amz_sku.id, 'name': asin,
                                            'clicks': 0, 'impressions': 0, 'cost': 0, 'sales': 0})

        DiscKeyCamp_df = pd.DataFrame(sp_sb_camp_key_data)
        DiscProCamp_df = pd.DataFrame(sp_sb_camp_pro_data)
        return DiscKeyCamp_df, DiscProCamp_df

    def get_live_sp_fetch_camp_df(self, targets_data):
        sp_camp_pro_data = []
        sp_camp_key_data = []

        live_campaigns = AmzSpAdsCamp.objects.filter(
            state='enabled', name__icontains='fetch')  # .exclude(targeting_type='auto')

        live_key_campaigns = live_campaigns.filter(name__icontains='key')
        live_pro_campaigns = live_campaigns.filter(name__icontains='pro')
        for campaign in live_key_campaigns:
            camp_targets = AmzSpAdsTarget.objects.filter(
                campaign__campaign_id_code=campaign.campaign_id_code)
            if camp_targets:
                ad_group_ids = camp_targets.values(
                    'ad_group_id_code').distinct()
                if len(ad_group_ids) > 1:
                    raise ValueError("More than one ad_group_id_code found.")
                elif len(ad_group_ids) == 1:
                    ad_group_id = ad_group_ids[0]['ad_group_id_code']
                else:
                    raise ValueError("No ad_group_id_code found.")

                # Create SPDiscProCamp/SBDiscProCamp object if targets exist
                sku_id = campaign.amz_sku.id if campaign.amz_sku else None
                sp_camp_key_data.append({'campaign': campaign.id, 'name': campaign.name, 'budget': campaign.budget,
                                        'campaign_id_code': campaign.campaign_id_code, 'ad_group_id_code': ad_group_id, 'amz_sku': sku_id})
                if sku_id == None:
                    print(campaign.id, "sku is none")
                    continue
                # Create AmzSkuDiscProTgt objects for each target
                for target in camp_targets:
                    exp = target.expression
                    # print(exp)
                    targets_data.append({'sku': target.campaign.amz_sku.id, 'name': exp,
                                        'clicks': 0, 'impressions': 0, 'cost': 0, 'sales': 0})

        for campaign in live_pro_campaigns:
            camp_targets = AmzSpAdsTarget.objects.filter(
                campaign__campaign_id_code=campaign.campaign_id_code)
            if camp_targets:
                ad_group_ids = camp_targets.values(
                    'ad_group_id_code').distinct()
                if len(ad_group_ids) > 1:
                    raise ValueError("More than one ad_group_id_code found.")
                elif len(ad_group_ids) == 1:
                    ad_group_id = ad_group_ids[0]['ad_group_id_code']
                else:
                    raise ValueError("No ad_group_id_code found.")

                # Create SPDiscProCamp/SBDiscProCamp object if targets exist
                sku_id = campaign.amz_sku.id if campaign.amz_sku else None
                sp_camp_pro_data.append({'campaign': campaign.id, 'name': campaign.name, 'budget': campaign.budget,
                                        'campaign_id_code': campaign.campaign_id_code, 'ad_group_id_code': ad_group_id, 'amz_sku': sku_id})
                if sku_id == None:
                    print(campaign.id, "sku is none")
                    continue
                # Create AmzSkuDiscProTgt objects for each target
                for target in camp_targets:
                    # exp = ast.literal_eval(target.expression)
                    exp = target.expression
                    # print(exp)
                    targets_data.append({'sku': target.campaign.amz_sku.id, 'name': exp,
                                        'clicks': 0, 'impressions': 0, 'cost': 0, 'sales': 0})

        key_camp = pd.DataFrame(sp_camp_key_data)
        pro_camp = pd.DataFrame(sp_camp_pro_data)
        return key_camp, pro_camp

    def sync_live_camp_and_target(self):
        """
        This method will sync SPDiscKeyCamp, SPDiscProCamp, SBDiscKeyCamp, SBDiscProCamp, SpDiscFetchKeyCamp, SpDiscFetchProCamp these models with initial
        live camps for both SP and SB additionally it method will sync AmzSkuDiscKey, AmzSkuDiscProTgt these
        models with initial live keys and pro.
        """
        keywords_data = []
        targets_data = []


        SBDiscKeyCamp_df, SBDiscProCamp_df = self.get_disc_sp_sb_camp_df(
            keywords_data, targets_data, "sb")
        SBDiscKeyCamp.manager.dfdb.sync(SBDiscKeyCamp_df)
        SBDiscProCamp.manager.dfdb.sync(SBDiscProCamp_df)

        SPDiscKeyCamp_df, SPDiscProCamp_df = self.get_disc_sp_sb_camp_df(
            keywords_data, targets_data, "sp")
        SPDiscKeyCamp.manager.dfdb.sync(SPDiscKeyCamp_df)
        SPDiscProCamp.manager.dfdb.sync(SPDiscProCamp_df)

        key_camp, pro_camp = self.get_live_sp_fetch_camp_df(targets_data)
        SpDiscFetchKeyCamp.manager.dfdb.sync(key_camp)
        SpDiscFetchProCamp.manager.dfdb.sync(pro_camp)

        keywords_df = pd.DataFrame(keywords_data)
        targets_df = pd.DataFrame(targets_data)

        # Drop duplicates from keywords_data and targets_data based on SKU and name
        AmzSkuDiscKey_df = keywords_df.drop_duplicates(subset=['sku', 'name'])
        AmzSkuDiscProTgt_df = targets_df.drop_duplicates(
            subset=['sku', 'name'])
        AmzSkuDiscKey.manager.dfdb.sync(AmzSkuDiscKey_df)
        AmzSkuDiscProTgt.manager.dfdb.sync(AmzSkuDiscProTgt_df)

    def __sync_disc_key(self, disc_campaign, live_key, disc_sku_tgt):
        # in this we cant add those camp keys wchich r not associated with any sku
        camps = disc_campaign.objects.filter(
            campaign__isnull=False, campaign__state='enabled', campaign__amz_sku__isnull=False)
        data = []
        for camp in camps:
            keywords = live_key.objects.filter(
                campaign__campaign_id_code=camp.campaign.campaign_id_code, match_type='exact', campaign__amz_sku__isnull=False)
            if keywords:
                for key in keywords:
                    sku_disc_tgt = disc_sku_tgt.objects.get(
                        sku=key.campaign.amz_sku.id, name=key.keyword_text)
                    # if not key.bid:
                    #     print({'sku_disc_tgt': sku_disc_tgt.id,'sku_disc_tgt_name' : sku_disc_tgt.name, 'disc_campaign' : camp.id,'disc_campaign_name' : camp.name, 'keyword' : key.id,'keyword_name' : key.keyword_text, 'bid' : key.bid, "keyword_id_code": key.keyword_id_code})
                    #     raise ValueError("Bid is nan.")
                    data.append({'sku_disc_tgt': sku_disc_tgt.id, 'disc_campaign': camp.id, 'keyword': key.id, 'bid': key.bid,
                                "keyword_id_code": key.keyword_id_code, "target_name": key.keyword_text, "amz_sku": key.campaign.amz_sku.id})

        df = pd.DataFrame(data)
        return df

    def __sync_disc_pro(self, disc_campaign, live_tar, disc_sku_tgt, camp_type):
        camps = disc_campaign.objects.filter(
            campaign__isnull=False, campaign__state='enabled', campaign__amz_sku__isnull=False)
        data = []
        xy = []
        if camp_type == "sp":
            asin_category = 'asin_same_as'
        else:
            asin_category = 'asinsameas'
        for camp in camps:
            targts = live_tar.objects.filter(
                campaign=camp.campaign, campaign__amz_sku__isnull=False)
            for key in targts:
                exp = ast.literal_eval(key.expression)
                _sku = key.campaign.amz_sku.id
                if 'value' in exp[0] and exp[0]['type'].lower() == asin_category:
                    asin = exp[0]['value']
                    sku_disc_tgt = disc_sku_tgt.objects.get(
                        sku=_sku, name=asin)
                    # print({'sku_disc_tgt' : sku_disc_tgt.id,'sku_disc_tgt_name' : sku_disc_tgt.name, 'disc_campaign' : camp.id,'disc_campaign_name' : camp.name,  'target' : key.id,'target_expression' : key.expression, 'bid' : key.bid, "target_id_code": key.target_id_code})
                    data.append({'sku_disc_tgt': sku_disc_tgt.id, 'disc_campaign': camp.id, 'target': key.id,
                                'bid': key.bid, "target_id_code": key.target_id_code, "target_name": asin, "amz_sku": _sku})
                elif 'value' in exp[0] and exp[0]['type'] == "ASIN_EXPANDED_FROM":
                    xy.append({'amz_sku': _sku, 'sku_disc_tgt_name': sku_disc_tgt.name, 'disc_campaign': camp.id, 'disc_campaign_name': camp.name,
                              'target': key.id, 'target_expression': key.expression, 'bid': key.bid, "target_id_code": key.target_id_code})
                    continue
                else:
                    sku_disc_tgt = disc_sku_tgt.objects.get(
                        sku=_sku, name=key.expression)
                    # print({'sku' : _sku ,'sku_disc_tgt_name' : sku_disc_tgt.name, 'disc_campaign' : camp.id,'disc_campaign_name' : camp.name,  'target' : key.id,'target_expression' : key.expression, 'bid' : key.bid, "target_id_code": key.target_id_code})
                    data.append({'sku_disc_tgt': sku_disc_tgt.id, 'disc_campaign': camp.id, 'target': key.id, 'bid': key.bid,
                                "target_id_code": key.target_id_code, "target_name": key.expression, "amz_sku": _sku})
        print(xy)
        df = pd.DataFrame(data)
        return df

    def sync_sb_sp_disc_key_pro(self):
        """
        This method will sync SBDiscKeyTgt, SBDiscProTgt, SPDiscKeyTgt, SPDiscProTgt these models with intial live keys and pro
        specificaly for one camapign type
        """
        # for SB, key nd pro
        key_df_sb = self.__sync_disc_key(
            disc_campaign=SBDiscKeyCamp, live_key=AmzSbAdsKeyword, disc_sku_tgt=AmzSkuDiscKey)
        SBDiscKeyTgt.manager.dfdb.sync(key_df_sb)

        pro_df_sb = self.__sync_disc_pro(
            disc_campaign=SBDiscProCamp, live_tar=AmzSbAdsTarget, disc_sku_tgt=AmzSkuDiscProTgt, camp_type="sb")
        SBDiscProTgt.manager.dfdb.sync(pro_df_sb)

        # for SP, key nd pro
        key_df_sp = self.__sync_disc_key(
            disc_campaign=SPDiscKeyCamp, live_key=AmzSpAdsKeyword, disc_sku_tgt=AmzSkuDiscKey)
        # we have to handle this case also, where keywords dont have matrix then its bid is nan
        key_df_sp['bid'] = key_df_sp['bid'].fillna(1.0)
        SPDiscKeyTgt.manager.dfdb.sync(key_df_sp)

        pro_df_sp = self.__sync_disc_pro(
            disc_campaign=SPDiscProCamp, live_tar=AmzSpAdsTarget, disc_sku_tgt=AmzSkuDiscProTgt, camp_type="sp")
        pro_df_sp['bid'] = pro_df_sp['bid'].fillna(1.0)
        SPDiscProTgt.manager.dfdb.sync(pro_df_sp)

    def populate_disc_models_with_live_data(self):
        """
        This method will sync all the 10 models, with live data. [4 camp models(SBDiscKeyCamp, SBDiscProCamp, SPDiscKeyCamp, SPDiscProCamp)],
        [2 sku discovered targets(AmzSkuDiscKey, AmzSkuDiscProTgt)] and [4 discovered camp targets(
        SPDiscKeyTgt, SPDiscProTgt, SBDiscKeyTgt, SBDiscProTgt)]
        """
        # this will populate AmzSkuDisc model and DiscCamp with live data
        self.sync_live_camp_and_target()
        # this will populate discovered key and pro for particular campaign(SB or SP)
        self.sync_sb_sp_disc_key_pro()
