import pandas as pd
import gzip
import csv


class BaseAmzAdsPerformanceRptUpdateSubManagerReportModdel:

    def _update_foreign_field_cols(self, df, foreign_fields):
        for col in foreign_fields:
            df[col] = df[col].apply(
                lambda x: {foreign_fields[col]: x} if x else {})

    def _check_date(self, df, report_type):
        # Check date is unique
        if not 'date' in df.columns:
            raise ValueError(
                'Date column not found in the file. Available columns are: %s, report_type: %s' % (df.columns, report_type))
        date = df['date'].unique()
        if len(date) > 1:
            raise ValueError('Date is not unique in the file')
        return date[0]

    def _get_qs(self, report_type, qs=None):
        if qs.exclude(report_type=report_type).exists():
            raise ValueError(
                'Invalid report type provided. The qs contained report types other than %s' % report_type)
        return qs

    def _insert_rpt(self, report_type, qs=None):
        qs = self._get_qs(report_type, qs)
        for i in qs:
            df = i.read_file()
            if df.empty:
                i._save_on_process(is_empty=True)
                continue
            date = self._check_date(df, report_type)
            self.manager.model.objects.filter(date=date).delete()
            try:
                if report_type=='sp_tgt':
                    self.manager.dfdb.sync(self._transform_df(df))
                else:
                    self.manager.dfdb.sync(self._transform_df(df))
                i._save_on_process(is_empty=False)
            except Exception as e:
                i._save_on_process(is_empty=False, error_message=str(e))
