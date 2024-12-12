class AmzAdsApiSubManagerMixinAdsTarget:
    def _rephrase_fk_campaign(self, df):
        df['campaign'] = df['campaignId'].apply(
            lambda x: {'campaign_id_code': x} if x else {})
        df.drop(columns=['campaignId'], inplace=True)
        return df

    def _rename_cols_for_keywords(self, df):
        df.rename(columns={'keywordId': 'keyword_id_code',
                           'adGroupId': 'ad_group_id_code'}, inplace=True)
        return df

    def _rename_cols_for_targets(self, df):
        df.rename(columns={'targetId': 'target_id_code',
                           'expressions': 'expression',
                           'adGroupId': 'ad_group_id_code'}, inplace=True)
        return df

    def _transform_keywords_df(self, df):
        df = self._rename_cols_for_keywords(df)
        df = self._rephrase_fk_campaign(df)
        return df

    def _transform_targets_df(self, df):
        df = self._rename_cols_for_targets(df)
        df = self._rephrase_fk_campaign(df)
        return df

