import asyncio
from sp_api.base import SellingApiRequestThrottledException
from sp_api.base.marketplaces import Marketplaces
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
from kn_api._kn_sp_api.reports import Reports
from core.utils.main import get_rate_limiter
from aiolimiter import AsyncLimiter

MAX_RETRY = 3


class AmzSpApiReportBaseFetcher:
    def __init__(self, marketplace: Marketplaces, *args, **kwargs):
        self.client = Reports(marketplace=marketplace)

    def _get_date_chunks(self, createdSince: datetime, createdUntil: datetime):
        chunks = []
        while createdSince < createdUntil:
            end_date = createdSince + relativedelta(days=30)
            if end_date > createdUntil:
                end_date = createdUntil
            chunks.append((createdSince, end_date))
            createdSince = end_date

        return chunks

    def create_report(self, reportType, dataStartTime, dataEndTime=None, **kwargs):
        if dataEndTime is None:
            dataEndTime = datetime.now()
        print(f"Fetching reports from {dataStartTime} to {dataEndTime}")
        dataEndTime = dataEndTime.isoformat()
        dataStartTime = dataStartTime.isoformat()
        return self.client.create_report(
            reportType=reportType,
            dataStartTime=dataStartTime,
            dataEndTime=dataEndTime,
            **kwargs,
        )

    def fetch_report_by_id(self, reportId):
        MAX_RETRY = 200
        while MAX_RETRY > 0:
            data = self.client.get_report(reportId=reportId)
            if data.payload["processingStatus"] == "DONE":
                print(data.payload["processingStatus"])
                break
            elif data.payload["processingStatus"] in {"FATAL", "CANCELLED"}:
                print(data.payload["processingStatus"])
                raise ValueError(f"{data.payload['processingStatus']} Error Occurred")
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
        for _ in range(MAX_RETRY):
            try:
                init_response = self.client.get_reports(
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
                    response = self.client.get_reports(nextToken=next_token)
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
                    lambda: self.client.get_report_document(
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
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
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
                    # Wait for the rate limiter to reset
                    time.sleep(time_period)
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
