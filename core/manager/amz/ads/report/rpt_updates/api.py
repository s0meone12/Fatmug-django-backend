from core.apis.clients import ADS_FETCHER
from datetime import datetime, timedelta
import uuid
from django.db import transaction
from core.manager.base import CheckQSMeta
from django.db.models.functions import TruncDate


class AmzAdsApiSubManagerAmzAdsPerformanceRptUpdate(metaclass=CheckQSMeta):
    def __init__(self, manager):
        self.manager = manager
        self.sb_client = ADS_FETCHER.AMZ_ADS_FETCHER_IN.sb
        self.sd_client = ADS_FETCHER.AMZ_ADS_FETCHER_IN.sd
        self.sp_client = ADS_FETCHER.AMZ_ADS_FETCHER_IN.sp
        self.model = self.manager.model

    def __get_report_id(self, report_type, date):
        if report_type == 'sb_tgt':
            return self.sb_client.post_report_v2_targeting(date)
        elif report_type == 'sb_st':
            return self.sb_client.post_report_v2_searchterm(date)
        elif report_type == 'sd_mt_at':
            return self.sd_client.post_report_v2_at_matched_target(date)
        elif report_type == 'sd_mt_ct':
            return self.sd_client.post_report_v2_ct_matched_target(date)
        elif report_type == 'sp_st':
            return self.sp_client.post_report_v3_searchterm(date)
        elif report_type == 'sp_tgt':
            return self.sp_client.post_report_v3_targeting(date)
        else:
            raise ValueError('Invalid report type')

    def _fetch_rpt_with_rpt_id(self, report_type, report_id):
        if report_type in ['sb_tgt', 'sb_st']:
            return self.sb_client._get_report_v2_from_id(report_id, report_client=self.sb_client._report_client)
        elif report_type in ['sd_mt_at', 'sd_mt_ct']:
            return self.sd_client._get_report_v2_from_id(report_id, report_client=self.sd_client._report_client)
        elif report_type in ['sp_st', 'sp_tgt']:
            return self.sp_client._get_report_v3_from_id(report_id, report_client=self.sp_client._report_client)
        else:
            raise ValueError('Invalid report type')

    def __dates_for_performance_reports(self, days=14):
        dates = [datetime.today().date() - timedelta(days=i+1)
                 for i in range(days+1)]
        till_date = self.manager.filter(
            source='gdrive').order_by('-date')
        till_date = till_date[0].date if till_date else dates[-1]
        final_dates = []
        for date in dates:
            if date > till_date:
                final_dates.append(date)
        return final_dates

    def __create_rpt__amz(self, date, report_type, report_id_code):
        prefixes = {
            'sb_tgt': 'sb_targeting_',
            'sb_st': 'sb_search_term_',
            'sp_st': 'sp_search_term_',
            'sp_tgt': 'sp_targeting_',
            'sd_mt_at': 'sd_matched_target_at_',
            'sd_mt_ct': 'sd_matched_target_ct_',
        }
        if report_type not in prefixes:
            raise ValueError('Invalid report type')
        file_name = prefixes[report_type] + str(uuid.uuid4()) + '.csv.gz'
        self.manager.create(
            date=date,
            source='api',
            report_type=report_type,
            name=file_name,
            report_id_code=report_id_code,
            state='pending',
        )

    def link_rpt(self):
        report_types = ['sb_tgt', 'sb_st',
                        'sd_mt_at', 'sd_mt_ct', 'sp_st', 'sp_tgt']
        dates = self.__dates_for_performance_reports()
        qs = self.manager.filter(
            date__in=dates, report_type__in=report_types, source='api')
        should_create = False

        if not (qs):
            should_create = True
        elif qs.count() != len(dates)*len(report_types):
            should_create = True
        elif qs.annotate(created_date=TruncDate('created_at')).values('created_date').distinct().count() != 1:
            should_create = True
        elif qs.order_by('-created_at')[0].get_created_at().date() != datetime.today().date():
            should_create = True
        counter = 1
        if should_create:
            with transaction.atomic():
                qs.delete()
                for date in dates:
                    for report_type in report_types:
                        report_id = self.__get_report_id(
                            report_type, date)
                        print(
                            f'Report Type: {report_type}, Date: {date}, Report ID: {report_id}, Counter: {counter}')
                        self.__create_rpt__amz(date, report_type, report_id)
                        counter += 1

    def get_rpt(self, qs=None):
        qs = qs.filter(file='')
        for i in qs:
            i.get_rpt()

    def insert_rpt(self, qs=None):
        qs = qs.filter(state='pending')
        for i in qs:
            i.insert_rpt()
