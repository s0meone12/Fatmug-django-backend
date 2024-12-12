import asyncio

from sp_api.base import SellingApiRequestThrottledException
from sp_api.base.marketplaces import Marketplaces
from core.services.amz.sell.fetcher.base import AmzSellBaseFetcher
from datetime import datetime, timedelta

import time
from kn_api._kn_sp_api.reports import Reports
from core.utils.main import get_rate_limiter
from aiolimiter import AsyncLimiter


class AmzSellReportBaseFetcher(AmzSellBaseFetcher):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._client_reports = Reports(marketplace=Marketplaces.IN)

    def _create_report(self, report_type, from_date_time=None, to_date_time=None):
        return self._client_reports.create_report(
            reportType=report_type,
            dataStartTime=from_date_time,
            dataEndTime=to_date_time,
        )

    def _fetch_report_ids(self, report_type, num_of_reports):
        """
        Helper method to fetch report IDs based on report type and number of reports.

        Parameters:
            - report_type (str): The type of report.
            - num_of_reports (int): Number of reports to fetch.

        Returns:
            list: List of report IDs.
        """
        response = self._client_reports.get_reports(
            reportTypes=[report_type], pageSize=num_of_reports
        )
        return [report["reportId"] for report in response.json()["reports"]]

    def _get_report(self, report_id):
        MAX_RETRIES = 60
        SLEEP_TIME = 10  # in seconds
        time.sleep(SLEEP_TIME)
        for _ in range(MAX_RETRIES):
            response_get_report = self._client_reports.get_report(report_id)
            response_payload = response_get_report.payload
            processing_status = response_payload.get("processingStatus")
            if processing_status == "DONE":
                report_document_id = response_payload["reportDocumentId"]
                break
        if processing_status != "DONE":
            print(f"processingStatus for {report_id} did not update to DONE")
            return None
        return report_document_id

    def _get_report_document(self, document_id):
        response = self._client_reports.get_report_document(document_id)
        if response.status_code == 500:
            print(response.__dict__)
            return None
        else:
            print(response.payload)
        document_content = response.payload.get("document", "")

        # Detect the line delimiter used in the document
        line_delimiter = "\r\n" if "\r\n" in document_content else "\n"

        # Split the document into lines, then split each line by tabs
        parsed_data = [
            line.split("\t") for line in document_content.split(line_delimiter)
        ]

        return parsed_data

    def _get_combined_data_of_report_documents(
        self,
        report_type,
        from_date_time=None,
        to_date_time=None,
        list_of_report_ids=None,
    ):
        def _fetch_report_data(report_id):
            report_document_id = self._get_report(report_id)
            if report_document_id:
                _report_data = self._get_report_document(report_document_id)
                if _report_data:
                    # Remove any empty trailing row
                    if not _report_data[-1][0]:
                        _report_data.pop()
                    return _report_data
            return None

        list_of_data_list = []

        # If report IDs are given, retrieve and combine data based on the report IDs
        if list_of_report_ids and isinstance(list_of_report_ids, list):
            for index, report_id in enumerate(list_of_report_ids):
                report_data = _fetch_report_data(report_id)
                if report_data:
                    # Skip header row for all reports except the first one
                    if index > 0:
                        report_data = report_data[1:]
                    list_of_data_list.extend(report_data)
            return list_of_data_list

        # If from_date_time and to_date_time are not given, default to the last 30 days
        if not from_date_time or not to_date_time:
            to_date_time = datetime.now()
            from_date_time = to_date_time - timedelta(days=30)

        # Split the date range into 30-day intervals and retrieve reports for each interval
        MAX_INTERVAL_DAYS = 30
        total_days = (to_date_time - from_date_time).days
        num_intervals = (total_days + MAX_INTERVAL_DAYS - 1) // MAX_INTERVAL_DAYS

        for interval in range(num_intervals):
            interval_start = from_date_time + timedelta(
                days=interval * MAX_INTERVAL_DAYS
            )
            interval_end = min(
                interval_start + timedelta(days=MAX_INTERVAL_DAYS), to_date_time
            )

            create_report_retry = 0
            while create_report_retry < 3:
                create_report_resp = self._create_report(
                    report_type, interval_start.isoformat(), interval_end.isoformat()
                )

                if create_report_resp.status_code == 200:
                    report_id = create_report_resp.json()["reportId"]

                    fetch_report_data_retry = 0
                    while fetch_report_data_retry < 3:
                        report_data = _fetch_report_data(report_id)
                        if report_data:
                            # Skip header row for all reports except the first one
                            if interval > 0:
                                report_data = report_data[1:]
                            list_of_data_list.extend(report_data)
                            break
                        else:
                            fetch_report_data_retry += 1

                    break
                else:
                    retry_wait_sec = 30
                    create_report_retry += 1
                    time.sleep(retry_wait_sec)
                    if create_report_retry > 0:
                        print(
                            f"Error fetching report data from {interval_start} to {interval_end}"
                        )

            else:
                print("not able to generate report id")

        return list_of_data_list


MAX_RETRY = 3


class AmzSellReportBaseFetcherV3(AmzSellBaseFetcher):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._client_reports = Reports(marketplace=Marketplaces.IN)

    def create_report(self, reportType, dataStartTime, dataEndTime=None, **kwargs):
        if dataEndTime is None:
            dataEndTime = datetime.now()
        return self._client_reports.create_report(
            reportType=reportType,
            dataStartTime=dataStartTime,
            dataEndTime=dataEndTime,
            **kwargs,
        )

    def fetch_report_by_id(self, reportId):
        MAX_RETRY = 200
        while MAX_RETRY > 0:
            data = self._client_reports.get_report(reportId=reportId)
            if data.payload["processingStatus"] == "DONE":
                print(data.payload["processingStatus"])
                break
            print(data.payload["processingStatus"])
            MAX_RETRY -= 1
            time.sleep(1)
        else:
            raise TimeoutError("Something went wrong during report fetching by ID")
        return data.payload["reportDocumentId"]

    def _filter_reports_by(self, key: str, response) -> list[str]:
        return [report[key] for report in response.payload["reports"]]

    def _fetch_report_ids(
        self, key: str, reportTypes: list, pageSize: int = 100, **kwargs
    ) -> list[str]:
        # key = "reportId" | "reportDocumentId"
        list_ids = list()
        # Fetch the initial set of reports
        print(f"kwargs: {kwargs}")
        for _ in range(MAX_RETRY):
            try:
                init_response = self._client_reports.get_reports(
                    reportTypes=reportTypes, pageSize=pageSize, **kwargs
                )
            except SellingApiRequestThrottledException:
                print("Sleeping for the rate limiter to reset (INIT)")
                time.sleep(1 / 0.0222)
            else:
                print("INIT")
                list_ids.extend(self._filter_reports_by(key, init_response))
                print(len(list_ids))
                next_token = init_response.next_token
                print("Next Token:", next_token)
                break
        else:
            raise TimeoutError("Something went wrong during report ids fetching")
        # If nextToken exist fetch records from nextToken
        while next_token:
            for _ in range(MAX_RETRY):
                try:
                    response = self._client_reports.get_reports(nextToken=next_token)
                except SellingApiRequestThrottledException:
                    print("Sleeping for the rate limiter to reset (nextToken)")
                    time.sleep(1 / 0.0222)
                else:
                    list_ids.extend(self._filter_reports_by(key, response))
                    print(len(list_ids))
                    next_token = response.next_token
                    print(next_token)
                    break
            else:
                raise TimeoutError(
                    "Something went wrong during report ids nextToken fetching"
                )
        return list_ids

    async def _get_report_document(
        self, limiter: AsyncLimiter, report_document_id: str, **kwargs
    ) -> list[list[str]]:
        async with limiter:
            try:
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: self._client_reports.get_report_document(
                        report_document_id, **kwargs
                    ),
                )
            except Exception as e:
                print(f"Error fetching document for {report_document_id}, error: {e}")
                return report_document_id

            document_content = response.payload["document"]
            # Detect the line delimiter used in the document
            line_delimiter = "\r\n" if "\r\n" in document_content else "\n"

            # Split the document into lines, then split each line by tabs
            parsed_data = [
                line.split("\t") for line in document_content.split(line_delimiter)
            ]
            if not parsed_data[-1][-1]:
                parsed_data.pop()
            print(f"Fetched document for: {report_document_id}")
            return parsed_data

    async def _get_combined_data_of_report_documents(
        self, limiter: AsyncLimiter, report_document_ids: list = None
    ):
        if report_document_ids and isinstance(report_document_ids, list):
            tasks = [
                self._get_report_document(
                    limiter, report_document_id, download=True, decrypt=True
                )
                for report_document_id in report_document_ids
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            # Filter out values
            success = list()
            failed = list()
            for result in results:
                if isinstance(result, list):
                    success.append(result)
                elif isinstance(result, str):
                    failed.append(result)
                else:
                    print(f"Unknown Error: {result} type: {type(result)}")
                    raise ValueError(f"Unknown Error: {result} type: {type(result)}")
            print(f"Success: {len(success)}, Failed: {len(failed)}")
            return success, failed

    def fetch_reports(
        self,
        report_document_ids: list,
        max_rate: int = 15,
        request_per_second: float = 0.0167,
    ) -> list:
        rate_limit = get_rate_limiter(max_rate, request_per_second)
        print(f"new")
        loop = asyncio.get_event_loop()
        success, failed = loop.run_until_complete(
            self._get_combined_data_of_report_documents(rate_limit, report_document_ids)
        )
        if failed:
            print(f"Fetching Failed Report Documents: Total {len(failed)}")
            time_period = 1 / rate_limit._rate_per_sec
            rate_limit = get_rate_limiter(
                1, time_period
            )  # Fetch failed report documents one at a time
            for report_document_id in failed:
                for _ in range(MAX_RETRY):  # Retry up to 3 times
                    time.sleep(time_period)  # Wait for the rate limiter to reset
                    loop = asyncio.get_event_loop()
                    _success, _failed = loop.run_until_complete(
                        self._get_combined_data_of_report_documents(
                            rate_limit, [report_document_id]
                        )
                    )
                    if _success:
                        success.extend(_success)
                        break
                    else:
                        print(
                            f"Retry failed for report document ID: {report_document_id}"
                        )
                else:
                    raise TimeoutError(
                        f"Failed to fetch report document ID: {report_document_id}"
                    )
            print(f"Final successfully fetched report documents: Total {len(success)}")

        list_of_all_reports = list()
        for index, data in enumerate(success):
            # Skip header row for all reports except the first one
            if index > 0:
                data = data[1:]
            list_of_all_reports.extend(data)
        return list_of_all_reports
