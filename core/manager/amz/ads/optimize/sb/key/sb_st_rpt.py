from core.models import AmzAdsSbStRpt
from ...mixin import ReportSubManagerMixinTgtOpt
import datetime
import pandas as pd
from .main import SbKeyTgtOptManager


class SbStReportSubManagerSbKeyTgtOpt(ReportSubManagerMixinTgtOpt):
    def __init__(self, manager: SbKeyTgtOptManager):
        self.model = AmzAdsSbStRpt
        self.manager = manager

    def sb_aggregated_data(self):
        optimize_periods = [7, 15, 180, 99999]
        final_df = pd.DataFrame()

        for optimize_period in optimize_periods:
            from_date = datetime.datetime.now().date(
            ) - datetime.timedelta(days=optimize_period)

            base_query = self.model.manager.filter(date__gte=from_date)
            df = self.model.manager.agg_data_for_opt_period(qs=base_query)
            if not df.empty:
                df = self.transform_optimize_df(
                    df=df, optimize_period=optimize_period, target_type='keyword')
                final_df = pd.concat([final_df, df], ignore_index=True)

        return self.manager.dfdb.sync(final_df)
