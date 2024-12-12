from django.db import models
from ....inheritance import BaseModel
from core.manager import AmzAdsPerformanceRptUpdateManager
from core.utils import Utils
from django.core.files.base import ContentFile
import gzip
import csv
import pandas as pd


class AmzAdsPerformanceRptUpdate(BaseModel):
    date = models.DateField(blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=255, blank=False,
                            null=False, unique=True)
    source = models.CharField(max_length=255, blank=False, null=False, choices=(
        ('gdrive', 'Google Drive'),
        ('api', 'API'),
    ))
    report_type = models.CharField(max_length=255, blank=False, null=False, choices=(
        ('sp_st', 'Sponsored Products Search Term'),
        ('sp_tgt', 'Sponsored Products Targeting'),

        ('sb_st', 'Sponsored Brands Search Term'),
        ('sb_tgt', 'Sponsored Brands Targeting'),

        ('sd_mt', 'Sponsored Display Targeting'),  # google drive
        ('sd_mt_at', 'Sponsored Display Targeting Attributed'),
        ('sd_mt_ct', 'Sponsored Display Targeting Click-Through'),
    ))
    report_id_code = models.CharField(max_length=255, blank=True, null=True)
    file = models.FileField(
        upload_to='amz_ads/rpt_files/', blank=False, null=False)
    state = models.CharField(max_length=255, choices=(
        ('pending', 'Pending'),
        ('processed', 'Processed'),
        ('error', 'Error'),
    ), default='pending', blank=False, null=False)
    error_message = models.TextField(null=True, blank=True)
    processed_file = models.FileField(
        upload_to='amz_ads/rpt_files/processed/', blank=True, null=True)
    is_empty = models.BooleanField(default=False)
    manager = AmzAdsPerformanceRptUpdateManager()

    class Meta:
        unique_together = ('date', 'report_type')

    def get_created_at(self):
        return Utils.convert_date_to_server_timezone(self.created_at)

    def get_rpt(self):
        if self.file:
            raise ValueError('File already exists for date: %s and report type: %s' % (
                self.date, self.report_type))
        df = self.__class__.manager.api._fetch_rpt_with_rpt_id(
            self.report_type, self.report_id_code)
        csv = df.to_csv(index=False)
        zip_file = gzip.compress(csv.encode('utf-8'))
        self.file = ContentFile(zip_file, name=self.name)
        self.save()
        print('File created for date: %s and report type: %s with name: %s' % (
            self.date, self.report_type, self.name))

    def __is_file_valid(self):
        file_path = self.file.path
        if file_path.endswith('.gz'):
            open_func = gzip.open
        else:
            open_func = open
        try:
            with open_func(file_path, 'rt', newline='', encoding='utf-8') as csvfile:
                # Read the first 1KB to check for CSV dialect
                start = csvfile.read(1024)
                dialect = csv.Sniffer().sniff(start)
                return True
        except (csv.Error, UnicodeDecodeError):
            # If an error is raised, the file might not be a CSV
            return False

    def __add_tactic_type_to_sd_mt(self, df):
        if self.report_type in ['sd_mt_at', 'sd_mt_ct']:
            if self.report_type == 'sd_mt_at':
                df['tactic_type'] = 'at'
            if self.report_type == 'sd_mt_ct':
                df['tactic_type'] = 'ct'
        return df

    def read_file(self):
        file = self.file
        if not self.__is_file_valid():
            raise ValueError(
                'File: {} is not a CSV file'.format(file.name))
        with gzip.open(file, 'rb') as f:
            first_line = f.readline()
            f.seek(0)
            if first_line.strip():
                df = pd.read_csv(f)
                df['date'] = self.date
                df = self.__add_tactic_type_to_sd_mt(df)
                return df
        return pd.DataFrame()

    def _save_on_process(self, is_empty=False, error_message=None):
        state = 'processed'
        if error_message:
            state = 'error'
        self.state = state
        self.is_empty = is_empty
        self.error_message = error_message
        self.save()

    def insert_rpt(self):
        if not self.file:
            raise ValueError('File does not exist for date: %s and report type: %s' % (
                self.date, self.report_type))
        if self.report_type == 'sb_st':
            from .sb_st import AmzAdsSbStRpt
            AmzAdsSbStRpt.manager.rpt_update.insert_rpt(qs=self)
        if self.report_type == 'sb_tgt':
            from .sb_tgt import AmzAdsSbTgtRpt
            AmzAdsSbTgtRpt.manager.rpt_update.insert_rpt(qs=self)
        if self.report_type == 'sp_st':
            from .sp_st import AmzAdsSpStRpt
            AmzAdsSpStRpt.manager.rpt_update.insert_rpt(qs=self)
        if self.report_type == 'sp_tgt':
            from .sp_tgt import AmzAdsSpTgtRpt
            AmzAdsSpTgtRpt.manager.rpt_update.insert_rpt(qs=self)
        if self.report_type in ['sd_mt_at', 'sd_mt_ct']:
            from .sd_mt import AmzAdsSdMtRpt
            AmzAdsSdMtRpt.manager.rpt_update.insert_rpt(qs=self)
