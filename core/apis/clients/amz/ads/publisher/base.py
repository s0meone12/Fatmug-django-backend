import pandas as pd

class AmzAdsBasePublisher:

    def _transform_camp_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        it will transform the df to the format that is required body by the API
        """
        
        campaign_id_mapping = df[['action_id', 'action__disc_campaign__campaign_id_code']].drop_duplicates()
        df_pivoted = df.pivot(index='action_id', columns='name', values='new_value').reset_index()
        df_pivoted.columns.name = None  # Remove the name of the index/columns for cleanliness
        df_pivoted = df_pivoted.astype(object).where(pd.notnull(df_pivoted), None)  # Replace NaN values with None
        # Merge to include campaign_id_code
        df_final = pd.merge(df_pivoted, campaign_id_mapping, on='action_id', how='left')
        # rename columns as needed
        df_final.rename(columns={
            "campaign_name": "name",
            "action__disc_campaign__campaign_id_code": "campaign_id_code"
        }, inplace=True)
        # add contant fields df 
        df_final["state"] = "ENABLED"
        df_final["budget"] = df_final["budget"].astype(float)
        return df_final

    def _transform_sb_key_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        it will transform the df to the format that is required body by the API
        """
        df.rename(columns={
            "disc_target__keyword_id_code": "keywordId",
            "disc_target__disc_campaign__campaign_id_code": "campaignId",
            "disc_target__disc_campaign__adgroup_id_code": "adGroupId",
            "disc_target__sku_disc_key__name": "keywordText",
            "disc_target__bid": "bid"
        }, inplace=True)
        df["matchType"] = "exact"
        df["keywordId"] = df["keywordId"].astype(int)
        df["campaignId"] = df["campaignId"].astype(int)
        df["adGroupId"] = df["adGroupId"].astype(int)
        return df

    def _transform_sb_pro_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        it will transform the df to the format that is required body by the API
        """
        df.rename(columns={
            "disc_target__target_id_code": "targetId",
            "disc_target__disc_campaign__campaign_id_code": "campaignId",
            "disc_target__disc_campaign__adgroup_id_code": "adGroupId",
            "disc_target__bid": "bid"
        }, inplace=True)
        df["state"] = "enabled"
        df["campaignId"] = df["campaignId"].astype(int)
        df["adGroupId"] = df["adGroupId"].astype(int)
        return df
    
    def _transform_sp_pro_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        it will transform the df to the format that is required body by the API
        """
        df.rename(columns={
            "disc_target__target_id_code": "targetId",
            "disc_target__disc_campaign__campaign_id_code": "campaignId",
            "disc_target__disc_campaign__adgroup_id_code": "adGroupId",
            "disc_target__sku_disc_pro__name": "value",
            "disc_target__bid": "bid"
        }, inplace=True)
        df["type"] = "ASIN_SAME_AS"
        df["expression"] = df.apply(lambda row: [{"type": row["type"], "value": row["value"]}], axis=1)
        return df
    
    def _transform_sp_key_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        it will transform the df to the format that is required body by the API
        """
        df.rename(columns={
            "disc_target__keyword_id_code": "keywordId",
            "disc_target__bid": "bid"
        }, inplace=True)
        df["state"] = "ENABLED"
        return df