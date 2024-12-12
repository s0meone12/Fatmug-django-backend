from datetime import datetime, timedelta
import pandas as pd
from core.apis.clients.amz.sell.reports.base import AmzSpApiReportBaseFetcher
from sp_api.base.marketplaces import Marketplaces


class SaleOrderReportFetcher(AmzSpApiReportBaseFetcher):
    def __init__(self, marketplace: Marketplaces, *args, **kwargs):
        super().__init__(marketplace, *args, **kwargs)

    def get_report(
        self,
        from_days_ago: int | None = None,
        to_days_until: int | None = 0,
        **kwargs,
    ) -> pd.DataFrame:
        report_type = "GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL"
        if from_days_ago is None:
            from_days_ago = 30
        if to_days_until is None:
            to_days_until = 0
        now = datetime.now()
        createdSince = now - timedelta(days=from_days_ago)
        createdUntil = now - timedelta(days=to_days_until)
        date_chunks = self._get_date_chunks(createdSince, createdUntil)
        df_list = list()
        for date_chunk in date_chunks:
            data = self.create_report(
                report_type,
                dataStartTime=date_chunk[0],
                dataEndTime=date_chunk[1],
            )
            reportId = data.payload["reportId"]
            reportDocumentId = self.fetch_report_by_id(reportId)
            print(f"Report Document Id: {reportDocumentId}")
            data = self.fetch_reports([reportDocumentId])
            df_list.append(pd.DataFrame(data[1:], columns=data[0]))
        for df in df_list:
            # print df length
            print(len(df))
        df = pd.concat(df_list)
        print(len(df))
        return df
