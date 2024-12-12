from ....df_db_handler import DataframeDBHandler
from core.models import AmzAdsPerformanceRptUpdate
import zipfile
import pandas as pd
from core.constants import PRE_API_AMZ_ADS_VARS
from datetime import datetime
from io import BytesIO
from django.core.files import File
from core.models import AmzSpAdsCamp, AmzSbAdsCamp, AmzSdAdsCamp, AmzSpAdsTarget, AmzSpAdsKeyword, AmzSbAdsTarget, AmzSbAdsKeyword, AmzSdAdsTarget, AmzAdsSpStRpt, AmzAdsSbTgtRpt, AmzAdsSdMtRpt, AmzAdsSpTgtRpt
from core.models.amz.ads.reports.sb_st import AmzAdsSbStRpt
import re


class AmzAdsPreApiDataAggregationService:

    SP_CAMP_RENAMES = {
        'Fetch_600427SWBGA1_B0BTLDS4QK_Pro': 'Fetch_600427_B0BTLDS4QK_Pro',
        'Fetch_600429SWBGA1_B0BTLBQMKR_Pro': 'Fetch_600429_B0BTLBQMKR_Pro',
        'Fetch_600426SWBGA1_B0BTLCJSRZ_Pro': 'Fetch_600426_B0BTLCJSRZ_Pro',
        'Fetch_600431SWBGA1_B0BTLBQ7DQ_Pro': 'Fetch_600431_B0BTLBQ7DQ_Pro',
        'Fetch_600428SWBGA1_B0BTLC23QK_Pro': 'Fetch_600428_B0BTLC23QK_Pro',
        'Fetch_600430SWBGA1_B0BTLD2611_Pro': 'Fetch_600430_B0BTLD2611_Pro',
    }

    EXCLUDE_SP_MATCHES = [
        "Fetch_600211_B08LNK3D77_Key[{'type': 'ASIN_SUBSTITUTE_RELATED'}]",
        'Fetch_700013SWHQ28_B07MF82BG4_Probird spikesPHRASE',
    ]

    def __init__(self):
        self.db_handler = DataframeDBHandler()

    def __add_camp_ids(self, df, report_type):

        if report_type == 'sp_st':
            df_of_camps_in_db = pd.DataFrame(list(AmzSpAdsCamp.objects.all().values(
                'name', 'id')))
            df['campaign_name'] = df['campaign_name'].replace(
                self.SP_CAMP_RENAMES)
        elif report_type == 'sb_st':
            df_of_camps_in_db = pd.DataFrame(list(AmzSbAdsCamp.objects.all().values(
                'name', 'id')))
        elif report_type == 'sd_mt':
            df_of_camps_in_db = pd.DataFrame(list(AmzSdAdsCamp.objects.all().values(
                'name', 'id')))
        elif report_type == 'sp_tgt':
            df_of_camps_in_db = pd.DataFrame(list(AmzSpAdsCamp.objects.all().values(
                'name', 'id')))
            df['campaign_name'] = df['campaign_name'].replace(
                self.SP_CAMP_RENAMES)
        else:
            raise ValueError(f"Unsupported report type: {report_type}")
        df_of_camps_in_db.rename(
            columns={'name': 'campaign_name'}, inplace=True)
        df = df.merge(df_of_camps_in_db,
                        on='campaign_name', how='left')
        if df['id'].isnull().sum() > 0:
            raise ValueError("Some campaigns: {} are not in the database".format(
                df[df['id'].isnull()]['campaign_name'].unique()))
        df.rename(columns={'id': 'campaign_id'}, inplace=True)
        return df

    def __add_target_ids_for_sp_tgt_rpt_tgt(self, df):
        def add_resolved_expression(row):
            if 'asin-expanded=' in row:
                value = row.split(
                    'asin-expanded="')[1].split('"')[0]
                value = [
                    {'type': 'ASIN_EXPANDED_FROM', 'value': value}]
            elif 'category=' in row:
                value = row.split('category="')[1].split('"')[0]
                if 'Organisers' in value:
                    value = value.replace(
                        'Organisers', 'Organizers')
                value = [
                    {'type': 'ASIN_CATEGORY_SAME_AS', 'value': value}]
            elif 'asin=' in row:
                value = row.split('asin="')[1].split('"')[0]
                value = [{'type': 'ASIN_SAME_AS', 'value': value}]
            elif row == 'substitutes':
                value = [{'type': 'ASIN_SUBSTITUTE_RELATED'}]
            elif row == 'close-match':
                value = [{'type': 'QUERY_HIGH_REL_MATCHES'}]
            elif row == 'complements':
                value = [{'type': 'ASIN_ACCESSORY_RELATED'}]
            elif row == 'loose-match':
                value = [{'type': 'QUERY_BROAD_REL_MATCHES'}]
            else:
                raise ValueError(
                    f"Unsupported pattern found: {row}")
            return value
        df = df[df['is_product_target'] == True]
        df['targeting_new'] = df['targeting'].apply(
            add_resolved_expression)
        df_target_in_db = pd.DataFrame(list(AmzSpAdsTarget.objects.all().values(
            'campaign__name', 'resolved_expression', 'id')))
        df_target_in_db.rename(
            columns={'campaign__name': 'campaign_name'}, inplace=True)
        df['match_column'] = df['campaign_name'] + \
            df['targeting_new'].apply(str)
        df = df[df['match_column'].isin(
            self.EXCLUDE_SP_MATCHES) == False]
        df_target_in_db['match_column'] = df_target_in_db['campaign_name'] + \
            df_target_in_db['resolved_expression'].apply(str)
        df = df.merge(df_target_in_db,
                        on='match_column', how='left')
        if df['id'].isnull().sum() > 0:
            raise ValueError("Some targets: {} are not in the database".format(
                df[df['id'].isnull()]['match_column'].unique()))
        df.rename(columns={'id': 'target_id'}, inplace=True)
        return df

    def __add_target_ids_for_sp_tgt_rpt_key(self, df):
        df = df[df['is_product_target'] == False]
        df['match_column'] = df['campaign_name'] + \
            df['targeting'] + df['match_type']
        df = df[df['match_column'].isin(
            self.EXCLUDE_SP_MATCHES) == False]
        df_in_db = pd.DataFrame(list(AmzSpAdsKeyword.objects.all().values(
            'campaign__name', 'keyword_text', 'match_type', 'id')))
        df_in_db.rename(
            columns={'campaign__name': 'campaign_name'}, inplace=True)
        df_in_db['match_column'] = df_in_db['campaign_name'] + \
            df_in_db['keyword_text'] + \
            df_in_db['match_type'].str.upper()
        df = df.merge(df_in_db, on='match_column', how='left')
        if df['id'].isnull().sum() > 0:
            raise ValueError("Some targets: {} are not in the database".format(
                df[df['id'].isnull()]['match_column'].unique()))
        df.rename(columns={'id': 'keyword_id'}, inplace=True)
        return df

    def __add_target_ids_for_sb_st(self, df):
        def add_resolved_expression(row):
            if 'asin=' in row:
                value = row.split('asin="')[1].split('"')[0]
                value = [{'type': 'asinSameAs', 'value': value}]
            else:
                raise ValueError(
                    f"Unsupported pattern found: {row}")
            return value

        df = df[df['is_target'] == True]
        df_in_db = pd.DataFrame(list(AmzSbAdsTarget.objects.all().values(
            'campaign__name', 'resolved_expressions', 'id')))
        df_in_db.rename(
            columns={'campaign__name': 'campaign_name'}, inplace=True)
        df['targeting_new'] = df['targeting'].apply(
            add_resolved_expression)
        df['match_column'] = df['campaign_name'] + \
            df['targeting_new'].apply(str)
        df_in_db['match_column'] = df_in_db['campaign_name'] + \
            df_in_db['resolved_expressions'].apply(str)
        df = df.merge(df_in_db, on='match_column', how='left')
        if df['id'].isnull().sum() > 0:
            raise ValueError("Some targets: {} are not in the database".format(
                df[df['id'].isnull()]['match_column'].unique()))
        df.rename(columns={'id': 'target_id'}, inplace=True)
        return df

    def __add_keyword_ids_for_sb_st(self, df):
        df = df[df['is_target'] == False]
        df_in_db = pd.DataFrame(list(AmzSbAdsKeyword.objects.all().values(
            'campaign__name', 'keyword_text', 'match_type', 'id')))
        df_in_db.rename(
            columns={'campaign__name': 'campaign_name'}, inplace=True)
        df['match_column'] = df['campaign_name'] + \
            df['targeting'] + df['match_type']
        df_in_db['match_column'] = df_in_db['campaign_name'] + \
            df_in_db['keyword_text'] + \
            df_in_db['match_type'].str.upper()
        df = df.merge(df_in_db, on='match_column', how='left')
        if df['id'].isnull().sum() > 0:
            raise ValueError("Some targets: {} are not in the database".format(
                df[df['id'].isnull()]['match_column'].unique()))
        df.rename(columns={'id': 'keyword_id'}, inplace=True)
        return df

    def __add_target_ids_for_sd_mt(self, df):
        def camel_case_transform(input_str):
            components = input_str.split("-")
            return components[0] + ''.join(x.title() for x in components[1:])

        def add_resolved_expression(input_str):

            parts = input_str.split("=")

            if len(parts) < 2:
                raise ValueError(
                    f"Cannot match pattern for input: {input_str}")

            main_comp = parts[0]
            value = "=".join(parts[1:])

            value = value.strip('"')

            if main_comp == "asin":
                return [{"type": "asinSameAs", "value": value}]

            sub_comps = value.strip("()").split()
            parsed_sub_comps = []

            for comp in sub_comps:
                if "=" in comp:
                    key, val = comp.split("=")
                    parsed_sub_comps.append(
                        {"type": camel_case_transform(key), "value": val})
                else:
                    parsed_sub_comps.append(
                        {"type": camel_case_transform(comp)})

            return [{"type": main_comp, "value": parsed_sub_comps}]

        df['resolved_expression'] = df['targeting'].apply(
            add_resolved_expression)
        df_in_db = pd.DataFrame(list(AmzSdAdsTarget.objects.all().values(
            'campaign__name', 'resolved_expression', 'id')))
        df_in_db.rename(
            columns={'campaign__name': 'campaign_name'}, inplace=True)
        df['match_column'] = df['campaign_name'] + \
            df['resolved_expression'].apply(str)
        df_in_db['match_column'] = df_in_db['campaign_name'] + \
            df_in_db['resolved_expression'].apply(str)
        df = df.merge(df_in_db, on='match_column', how='left')
        if df['id'].isnull().sum() > 0:
            raise ValueError("Some targets: {} are not in the database".format(
                df[df['id'].isnull()]['match_column'].unique()))
        df.rename(columns={'id': 'target_id'}, inplace=True)
        return df

    def __clean_df(self, df, report_type):
        if report_type == 'sp_st':
            df = df[[
                'Date',
                'campaign_id',
                'Customer Search Term',
                'Impressions',
                'Clicks',
                'Spend',
                '7 Day Total Sales (₹)',
                '7 Day Total Units (#)',
                '7 Day Advertised SKU Units (#)',
                '7 Day Advertised SKU Sales (₹)',
            ]]
            df.rename(columns={
                'Date': 'date',
                'Customer Search Term': 'search_term',
                'Impressions': 'impressions',
                'Clicks': 'clicks',
                'Spend': 'cost',
                '7 Day Total Sales (₹)': 'sales_14d',
                '7 Day Total Units (#)': 'units_sold_clicks_14d',
                '7 Day Advertised SKU Units (#)': 'units_sold_same_sku_14d',
                '7 Day Advertised SKU Sales (₹)': 'attributed_sales_same_sku_14d',
            }, inplace=True)
            df = df.groupby(['date', 'campaign_id', 'search_term']).agg(
                {'impressions': 'sum', 'clicks': 'sum', 'cost': 'sum', 'sales_14d': 'sum', 'units_sold_clicks_14d': 'sum', 'units_sold_same_sku_14d': 'sum', 'units_sold_other_sku_14d': 'sum', 'attributed_sales_same_sku_14d': 'sum', 'sales_other_sku_14d': 'sum'}).reset_index()

        elif report_type == 'sb_st':
            df = df[[
                'Date',
                'campaign_id',
                'target_id',
                'keyword_id',
                'Impressions',
                'Clicks',
                'Spend',
                '14 Day Total Sales (₹)',
                '14 Day Total Units (#)',
            ]]
            df.rename(columns={
                'Date': 'date',
                'Impressions': 'impressions',
                'Clicks': 'clicks',
                'Spend': 'cost',
                '14 Day Total Sales (₹)': 'attributed_sales_14d',
                '14 Day Total Units (#)': 'units_sold_14d',
            }, inplace=True)
            df['target_id'].fillna(-1, inplace=True)
            df['keyword_id'].fillna(-1, inplace=True)
            df = df.groupby(['date', 'campaign_id', 'target_id', 'keyword_id']).agg(
                {'impressions': 'sum', 'clicks': 'sum', 'cost': 'sum', 'attributed_sales_14d': 'sum', 'units_sold_14d': 'sum'}).reset_index()
            df['target_id'].replace(-1, np.nan, inplace=True)
            df['keyword_id'].replace(-1, np.nan, inplace=True)

        elif report_type == 'sd_mt':
            df = df[[
                'Date',
                'campaign_id',
                'target_id',
                'Matched target',
                'Impressions',
                'Clicks',
                'Spend',
                '14 Day Total Sales (₹)',
                '14 Day Total Units (#)',
            ]]
            df.rename(columns={
                'Matched target': 'matched_target',
                'Impressions': 'impressions',
                'Clicks': 'clicks',
                'Spend': 'cost',
                '14 Day Total Sales (₹)': 'attributed_sales_14d',
                '14 Day Total Units (#)': 'attributed_units_ordered_14d',
                'Date': 'date',
            }, inplace=True)
            df = df.groupby(['date', 'campaign_id', 'target_id', 'matched_target']).agg(
                {'impressions': 'sum', 'clicks': 'sum', 'cost': 'sum', 'attributed_sales_14d': 'sum', 'attributed_units_ordered_14d': 'sum'}).reset_index()
        elif report_type == 'sp_tgt':
            df = df[[
                'Date',
                'campaign_id',
                'keyword_id',
                'target_id',
                'Impressions',
                'Clicks',
                'Spend',
                '7 Day Total Sales (₹)',
                '7 Day Total Units (#)',
                '7 Day Advertised SKU Units (#)',
                '7 Day Advertised SKU Sales (₹)',
            ]]
            df.rename(columns={
                'Date': 'date',
                'Impressions': 'impressions',
                'Clicks': 'clicks',
                'Spend': 'cost',
                '7 Day Total Sales (₹)': 'sales_14d',
                '7 Day Total Units (#)': 'units_sold_clicks_14d',
                '7 Day Advertised SKU Units (#)': 'units_sold_same_sku_14d',
                '7 Day Advertised SKU Sales (₹)': 'attributed_sales_same_sku_14d',
            }, inplace=True)
        else:
            raise ValueError(f"Unsupported report type: {report_type}")
        return df

    def __add_target_ids(self, df, report_type):
        if report_type == 'sp_tgt':
            df = df[df['targeting'].notnull()]
            df['is_product_target'] = df['targeting'].apply(
                lambda x: bool(re.search(r'\w+=".*', x)) or x in ['close-match', 'loose-match', 'complements', 'substitutes'])
            df_target = self.__add_target_ids_for_sp_tgt_rpt_tgt(df)
            df_key = self.__add_target_ids_for_sp_tgt_rpt_key(df)
            df = pd.concat([df_target, df_key])
        elif report_type == 'sp_st':
            # This has been commented out since we are not storing the target or keyword ids for sp_st only search terms
            # df['is_product_target'] = df['targeting'].apply(
            #     lambda x: bool(re.search(r'\w+=".*', x)) or x == '*')
            # df_key = add_target_ids_for_sp_st_rpt_key(df)
            # df_target = add_target_ids_for_sp_st_rpt_tgt(df)
            pass
        elif report_type == 'sb_st':
            df['is_target'] = df['targeting'].apply(
                lambda x: bool(re.search(r'\w+=".*', x)))
            df_target = self.__add_target_ids_for_sb_st(df)
            df_key = self.__add_keyword_ids_for_sb_st(df)
            df = pd.concat([df_target, df_key])
        elif report_type == 'sd_mt':
            df = self.__add_target_ids_for_sd_mt(df)
        else:
            raise ValueError(f"Unsupported report type: {report_type}")
        return df

    def __add_camp_n_target_ids(self, df, report_type):
        df = df.rename(
            columns={'Campaign Name': 'campaign_name', 'Targeting': 'targeting', 'Match Type': 'match_type'})
        self.__add_camp_ids(df, report_type)
        self.__add_target_ids(df, report_type)
        self.__clean_df(df, report_type)
        return df

    def __check_date_for_gdrive_rpt_df(self, df, instance):

        date_cols = PRE_API_AMZ_ADS_VARS['pre_api_report_date_columns'][instance.report_type]

        """
        Checks whether the date in the report is unique and matches the date on the instance.
        """
        # For reports with both start and end dates, we won't check against instance date
        if len(date_cols) == 2:
            start_date_col, end_date_col = date_cols
            if not df[start_date_col].equals(df[end_date_col]):
                raise ValueError(
                    "Start and end dates in the report are not the same.")
        date_col = date_cols[0]

        # Check if date column has unique value or no value
        if df[date_col].nunique() != 1:
            raise ValueError("Multiple dates found in the report.")

        # Check if that unique date matches the instance's date
        report_date = df[date_col].iloc[0]

        # Ensure the report_date is a date object
        if isinstance(report_date, datetime):
            report_date = report_date.date()
        elif isinstance(report_date, str):
            report_date = datetime.strptime(
                report_date, '%Y-%m-%d').date()

        if report_date != instance.date:
            raise ValueError(
                f"Date in the report ({report_date}) doesn't match the instance date ({instance.date}).")

    def process_pre_api_report_updates(self, qs=None):
        if qs is None:
            qs = AmzAdsPerformanceRptUpdate.objects.filter(
                processed_file='', source='gdrive')
        for instance in qs:
            file = instance.file
            with zipfile.ZipFile(file, 'r') as zipped_file:
                # Get the list of file names in the archive
                files_in_zip = zipped_file.namelist()

                # Check if there's only one file in the archive
                if len(files_in_zip) != 1:
                    raise ValueError(
                        "The zip archive should contain only one file")

                # Extract its name
                file_name = files_in_zip[0]

                # Open that file to read its content
                # try:
                with zipped_file.open(file_name) as extracted_file:
                    # Depending on the file extension, you can use appropriate pandas method to read it
                    if file_name.endswith('.csv'):
                        df = pd.read_csv(extracted_file)
                    elif file_name.endswith('.xls') or file_name.endswith('.xlsx'):
                        df = pd.read_excel(extracted_file)
                    else:
                        raise ValueError("Unsupported file format")

                    if not (df.empty):
                        # Check if the date in the report matches the date on the instance
                        self.__check_date_for_gdrive_rpt_df(df, instance)

                    if instance.report_type == 'sd_mt':
                        # If the report is sd_mt, then we need to convert start and end date to a single date column have the unique date since both start and end date are the same
                        df['Date'] = df['Start Date']
                        df.drop(columns=['Start Date',
                                'End Date'], inplace=True)
                    # Add Campaign ID and Keyword ID to the dataframe
                    df = self.__add_camp_n_target_ids(
                        df, instance.report_type)
                    # Create a BytesIO buffer to hold the zipped file
                    buffer = BytesIO()
                    with zipfile.ZipFile(buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
                        zip_file.writestr(instance.report_type +
                                            '.csv', df.to_csv(index=False))
                    buffer.seek(0)
                    # Save to Django model's FileField
                    instance.processed_file.save('data.zip', File(buffer))
                    instance.error_message = None
                    instance.state = 'pending'
                    instance.save()
                # except Exception as e:
                #     instance.error_message = str(e)
                #     instance.state = 'error'
                #     instance.processed_file = None
                #     instance.save()
                #     raise Exception(str(e) + " for file: " + file_name)

    def insert_pre_api_reports_into_models(self):
        report_types = ['sp_st', 'sb_st', 'sb_tgt', 'sd_mt', 'sp_tgt']
        for report_type in report_types:
            queryset = AmzAdsPerformanceRptUpdate.objects.filter(
                processed_file__isnull=False, source='gdrive', report_type=report_type)
            dates = queryset.values_list('date', flat=True)
            df = pd.DataFrame()
            try:
                for instance in queryset:
                    file = instance.processed_file
                    with zipfile.ZipFile(file, 'r') as zipped_file:
                        # Get the list of file names in the archives
                        files_in_zip = zipped_file.namelist()

                        # Check if there's only one file in the archive
                        if len(files_in_zip) != 1:
                            raise ValueError(
                                "The zip archive should contain only one file")

                        # Extract its name
                        file_name = files_in_zip[0]

                        # Open that file to read its content
                        with zipped_file.open(file_name) as extracted_file:
                            # Depending on the file extension, you can use appropriate pandas method to read it
                            if file_name.endswith('.csv'):
                                df_i = pd.read_csv(extracted_file)
                            elif file_name.endswith('.xls') or file_name.endswith('.xlsx'):
                                df_i = pd.read_excel(extracted_file)
                            else:
                                raise ValueError("Unsupported file format")
                            df = pd.concat([df, df_i])

                if not (df.empty):
                    df['id'] = None
                    report_type = instance.report_type
                    if report_type == 'sp_st':
                        AmzAdsSpStRpt.objects.filter(
                            date__in=dates).delete()
                        self.db_handler.db_sync(AmzAdsSpStRpt, df)
                    elif report_type == 'sb_st':
                        AmzAdsSbStRpt.objects.filter(
                            date__in=dates).delete()
                        self.db_handler.db_sync(AmzAdsSbStRpt, df)
                    elif report_type == 'sb_tgt':
                        AmzAdsSbTgtRpt.objects.filter(
                            date__in=dates).delete()
                        self.db_handler.db_sync(AmzAdsSbTgtRpt, df)
                    elif report_type == 'sd_mt':
                        AmzAdsSdMtRpt.objects.filter(
                            date__in=dates).delete()
                        self.db_handler.db_sync(AmzAdsSdMtRpt, df)
                    elif report_type == 'sp_tgt':
                        AmzAdsSpTgtRpt.objects.filter(
                            date__in=dates).delete()
                        self.db_handler.db_sync(AmzAdsSpTgtRpt, df)
                    else:
                        raise ValueError(
                            f"Unsupported report type: {report_type}")
                queryset.update(state='processed', error_message=None)
            except Exception as e:
                queryset.update(state='error', error_message=str(e))
