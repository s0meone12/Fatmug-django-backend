import time
import requests
import gzip
import json
import pandas as pd
from io import BytesIO
from datetime import datetime
import os


class AmzAdsBaseFetcher:
    """
        Base class for all fetchers.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _get_date(self, date=None):
        if date is None:
            date = datetime.now().date()
        return date

    def _get_date_str_v2(self, date=None):
        date = self._get_date(date)
        return date.strftime('%Y%m%d')

    def _get_date_str_v3(self, date=None):
        date = self._get_date(date)
        return date.strftime('%Y-%m-%d')

    def _post_report_v3(self, **kwargs):
        time.sleep(2)
        client_reports = kwargs.pop("report_client")
        body = kwargs.pop('body')
        body = json.dumps(body)
        res = client_reports.post_report(body=body, **kwargs).payload
        failure_reason = res.get('failureReason')
        if failure_reason:
            raise Exception(failure_reason)
        report_id = res.get('reportId')
        return report_id

    def _get_report_v3(self, report_id, **kwargs):
        client_reports = kwargs.get("report_client")
        status = 'PENDING'
        time.sleep(60)
        while status in ['PENDING', 'PROCESSING']:
            res = client_reports.get_report(
                reportId=report_id)
            status = res.payload.get('status')
            time.sleep(120)
        if status == 'COMPLETED':
            return res.payload.get('url')
        else:
            failure_reason = res.payload.get('failureReason')
            status = res.payload.get('status')
            # Raise detailed error whith failure reason and status
            raise Exception(
                f'Error getting report: {failure_reason} ({status})')

    def _get_report_v3_without_wait(self, report_id, **kwargs):

        status = None
        client_reports = kwargs.get('report_client')

        while status not in ['SUCCESS', "COMPLETED"]:
            res = client_reports.get_report(
                reportId=report_id)
            status = res.payload.get('status')
            time.sleep(5)

        if res.payload.get('location'):
            return res.payload.get('location')
        elif res.payload.get('url'):
            return res.payload.get('url')
        return None

    def _unpack_report_v3(self, url, **kwargs):
        # Fetch the GZIP content from the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Decompress the GZIP content
        with gzip.GzipFile(fileobj=BytesIO(response.content)) as gz:
            json_data = json.load(gz)

        # Convert the JSON data to a DataFrame
        df = pd.DataFrame(json_data)

        return df

    def _get_report_v3_data(self, **kwargs):
        report_id = self._post_report_v3(**kwargs)
        url = self._get_report_v3(report_id, **kwargs)
        df = self._unpack_report_v3(url)
        return df

    def _get_report_v3_from_id(self, report_id, **kwargs):
        url = self._get_report_v3_without_wait(report_id, **kwargs)
        if url is None:
            return None
        df = self._unpack_report_v3(url, **kwargs)
        return df

    def _post_report_v2(self, **kwargs):
        time.sleep(2)
        report_client = kwargs.pop("report_client")
        record_type = kwargs.pop('recordType')
        body = kwargs.pop('body')
        body = json.dumps(body)
        response = report_client.post_report(
            recordType=record_type, body=body, **kwargs)

        report_id = response.payload.get('reportId')
        return report_id

    def _get_report_v2(self, report_id, **kwargs):
        report_client = kwargs.get("report_client")
        status = 'IN_PROGRESS'
        time.sleep(60)
        while status == 'IN_PROGRESS':
            res = report_client.get_report(
                reportId=report_id)
            status = res.payload.get('status')
            time.sleep(120)
        if status != 'SUCCESS':
            failure_reason = res.payload.get('failureReason')
            status = res.payload.get('status')
            # Raise detailed error whith failure reason and status
            raise Exception(
                f'Error getting report: {failure_reason} ({status})')
        return res.payload.get('location')

    def _get_report_v2_without_wait(self, report_id):
        res = self.report_client.get_report(
            reportId=report_id)
        status = res.payload.get('status')
        if status != 'SUCCESS':
            return None
        return res.payload.get('location')

    def _unpack_report_v2(self, url, **kwargs):
        report_client = kwargs.pop("report_client")
        resp = report_client.download_report(
            url=url)
        response=resp.json()
        df = pd.DataFrame(response)
        return df

    def _get_report_v2_data(self, **kwargs):
        report_id = self._post_report_v2(**kwargs)
        url = self._get_report_v2(report_id, **kwargs)
        df = self._unpack_report_v2(url, **kwargs)
        return df

    def _get_report_v2_from_id(self, report_id, **kwargs):
        url = self._get_report_v3_without_wait(report_id, **kwargs)
        if url is None:
            return None
        df = self._unpack_report_v2(url, **kwargs)
        return df