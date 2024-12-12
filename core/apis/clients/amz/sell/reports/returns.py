from datetime import datetime, timedelta

import pandas as pd
from core.apis.clients.amz.sell.reports.base import AmzSpApiReportBaseFetcher
from sp_api.base.marketplaces import Marketplaces


class SaleReturnReportFetcher(AmzSpApiReportBaseFetcher):
    def __init__(self, marketplace: Marketplaces, *args, **kwargs):
        super().__init__(marketplace, *args, **kwargs)

    def get_report(self, from_days_ago: int | None = None, **kwargs) -> pd.DataFrame:
        # Fetch last start_from days of customer returns data, update as needed
        if from_days_ago is None:
            from_days_ago = 365
        report_type = "GET_FBA_FULFILLMENT_CUSTOMER_RETURNS_DATA"
        data = self.create_report(
            report_type, dataStartTime=datetime.now() - timedelta(days=from_days_ago)
        )
        print(data.payload)
        reportId = data.payload["reportId"]
        reportDocumentId = self.fetch_report_by_id(reportId)
        print(f"Report Document Id: {reportDocumentId}")
        data = self.fetch_reports([reportDocumentId])
        return pd.DataFrame(data[1:], columns=data[0])
