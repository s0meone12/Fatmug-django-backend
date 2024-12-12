import datetime


class ReportSubManagerMixinTgtOpt:
    """
    Base class for optimization services.
    """
    def transform_optimize_df(self, df, optimize_period, target_type):
        cols_to_rename = {
            '_impressions': 'impressions',
            '_clicks': 'clicks',
            f'{target_type}__{target_type}_id_code': 'disc_tgt'
        }
        df = df.rename(columns=cols_to_rename)
        df['date'] = datetime.datetime.now()
        df['opt_duration'] = optimize_period
        df['acos'] = df.apply(lambda row: round(row['spend'] / row['sales'], 3) if row['sales'] != 0 else round(row['spend'] / 99999, 3), axis=1)
        df['spend_after_mute'] = 0.0
        df['old_cpc'] = 0.0
        df['new_cpc'] = 0.0
        df['disc_tgt'] = df['disc_tgt'].apply(lambda x: {f'{target_type}_id_code': x})