class AmzSkuSubManagerMixinDiscTarget:

    def _discover(self, qs=None, model=None, method=None):
        df = getattr(model.manager.amz_sku, method)(qs=qs)
        if not df.empty:
            df = df[['id', 'name', 'sku_id']]
            df.rename(columns={
                'id': 'sku_disc_tgt',
                'name': 'target_name',
                'sku_id': 'amz_sku_id'
            }, inplace=True)
            self.manager.dfdb.sync(df)
