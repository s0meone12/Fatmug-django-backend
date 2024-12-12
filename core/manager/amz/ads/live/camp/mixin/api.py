class AmzAdsApiSubManagerMixinAdCamp:
    def _rename_cols_for_campaigns_df(self, df):
        rename_cols = {
            'campaignId': 'campaign_id_code',
            'brandEntityId': 'brand_entity_id_code',
        }
        for col in rename_cols:
            try:
                df.rename(columns={col: rename_cols[col]}, inplace=True)
            except:
                pass
        return df

    def _add_amz_sku_to_campaigns_df(self, df):
        df['asin'] = df['name'].apply(lambda asin: (asin.split(
            '_')[-2] if len(asin.split('_')) > 1 else '') if asin else '')
        df['amz_sku'] = df['asin'].apply(
            lambda asin: {'asin': asin} if asin else {})
        df.drop(columns=['asin'], inplace=True)
        return df

    def _transform_campaigns_df(self, df):
        df = self._add_amz_sku_to_campaigns_df(df)
        df = self._rename_cols_for_campaigns_df(df)
        if "tags" in df:
            df.drop(columns=['tags'], inplace=True)
        if "kpi" in df:
            df.drop(columns=['kpi'], inplace=True)
        return df

    def _transform_budget_col(self, df):
        selected_columns = ['budget', 'endDate', 'startDate', 'name',
                            'campaignId', 'state', 'dynamicBidding', 'targetingType']
        df = df[selected_columns]
        df['budget_original'] = df['budget']
        df.drop(columns=['budget'], inplace=True)
        df['budget'] = df['budget_original'].apply(
            lambda x: x['budget'])
        df['budgetType'] = df['budget_original'].apply(
            lambda x: x['budgetType'])
        df.drop(columns=['budget_original'], inplace=True)
        return df
