from datetime import datetime, timedelta

import pandas as pd
from core.apis.clients.amz.sell.reports.base import AmzSpApiReportBaseFetcher
from sp_api.base.marketplaces import Marketplaces


class SaleSettlementReportFetcher(AmzSpApiReportBaseFetcher):
    def __init__(self, marketplace: Marketplaces, *args, **kwargs):
        super().__init__(marketplace, *args, **kwargs)

    def get_report(
        self,
        createdSince: datetime | None = None,
        createdUntil: datetime | None = None,
        **kwargs,
    ) -> pd.DataFrame:
        # pass createdSince or it will fetch last 7 days settlement report data.
        report_type = "GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE_V2"
        if createdSince is None:
            createdSince = datetime.now() - timedelta(days=7)
        kwargs["createdSince"] = createdSince
        if createdUntil is None:
            createdUntil = datetime.now()
        kwargs["createdUntil"] = createdUntil
        print(f"Fetching Settlement Reports Since: {createdSince} to {createdUntil}")
        # Add constraint: createdSince must be before createdUntil
        if createdSince > createdUntil:
            raise ValueError("createdSince must be before createdUntil")
        report_ids = self._fetch_report_ids(
            "reportDocumentId", [report_type], 100, **kwargs
        )
        print(f"Reports To Fetch: {len(report_ids)}")
        data = self.fetch_reports(report_ids)
        return pd.DataFrame(data[1:], columns=data[0])
