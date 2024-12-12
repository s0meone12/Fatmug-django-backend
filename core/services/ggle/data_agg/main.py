from ..fetcher.base import GoogleBaseFetcher
from core.constants import PRE_API_AMZ_ADS_VARS
from datetime import date, timedelta
import pandas as pd
from core.models import AmzAdsPerformanceRptUpdate
from django.core.files import File
from django.db import transaction


class GoogleAmzAmdsDataAggregationService:

    def __init__(self, *args, **kwargs):
        self.fetcher = GoogleBaseFetcher()

    def df_of_amz_ads_performance_reports_in_db(self):
        """
        Returns a dataframe of the report files in the DB
        """
        df = pd.DataFrame(
            list(AmzAdsPerformanceRptUpdate.objects.all().values('name', 'report_type', 'date')))

        if df.empty:
            df = pd.DataFrame(columns=['name', 'report_type', 'date'])

        return df

    def __check_amz_ads_performance_rpt_files_exist(self, df_gd, df_db):
        def generate_date_range(start_date, till_date):
            end_date = date.today() - timedelta(days=7)
            if till_date > end_date:
                till_date = end_date
            date_range = []
            while start_date <= till_date:
                date_range.append(start_date)
                start_date += timedelta(days=1)
            return date_range

        till_date = PRE_API_AMZ_ADS_VARS['fetch_performance_rpt_from_gdrive_till_date']
        start_dates = PRE_API_AMZ_ADS_VARS['start_dates']

        missing_reports = {}

        for report_type, start_date in start_dates.items():
            df = pd.concat([df_gd[df_gd['report_type'] == report_type],
                            df_db[df_db['report_type'] == report_type]])
            df.drop_duplicates(subset=['name'], inplace=True)

            expected_dates = set(generate_date_range(start_date, till_date))
            present_dates = set(df['date'])
            missing_dates = expected_dates - present_dates

            if missing_dates:
                missing_reports[report_type] = missing_dates

        return missing_reports

    # @retry(stop=stop_after_attempt(3), wait=wait_fixed(180))
    def _sync_amz_ads_performance_report_updates(self):
        def create_db_entry(df_gd, df_db):
            """
            Creates a database entry for each report file from the Google Drive that doesn't exist in the DB.
            """
            # Anti-join to find rows in df_gd that are not in df_db
            merged_df = pd.merge(
                df_gd, df_db, on=['name', 'report_type', 'date'], how='left', indicator=True)
            to_create = merged_df[merged_df['_merge'] == 'left_only']

            creates = []
            # Create DB entries for each row in the filtered dataframe
            to_create.apply(create_db_record_for_row, axis=1, args=(creates,))
            # Bulk create the DB records
            with transaction.atomic():
                AmzAdsPerformanceRptUpdate.objects.bulk_create(creates)

        def create_db_record_for_row(row, creates):
            # Download the file from Google Drive
            file_io = self.fetcher.download_file_from_gdrive(row['id'])
            # Create the DB record
            report_file = AmzAdsPerformanceRptUpdate(
                date=row['date'],
                name=row['name'],
                source='gdrive',
                report_type=row['report_type'],
                # Save the downloaded file
                file=File(file_io, name=row['name']),
                state='pending',  # Default state is 'pending'
            )
            creates.append(report_file)
        df_gd = self.fetcher.df_amz_ads_performance_reports()
        df_db = self.df_of_amz_ads_performance_reports_in_db()
        missing_reports = self.__check_amz_ads_performance_rpt_files_exist(
            df_gd, df_db)
        if missing_reports:
            raise ValueError(
                f"Missing reports found: {missing_reports}")
        create_db_entry(df_gd, df_db)
