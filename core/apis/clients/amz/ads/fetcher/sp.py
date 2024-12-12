from .base import AmzAdsBaseFetcher
from kn_api._kn_ad_api.sp import CampaignsV3, KeywordsV3, TargetsV3, NegativeKeywordsV3, NegativeTargetsV3
from kn_api._kn_ad_api.sp.reports import Reports
from sp_api.base import Marketplaces
import requests,gzip,json,time,pandas as pd
from io import BytesIO


class AmzAdsSpFetcher(AmzAdsBaseFetcher):
    """
    Fetcher for Sponsored Products.
    """

    def __init__(self, marketplace:Marketplaces, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._client_campaigns = CampaignsV3(marketplace)
        self._client_keywords = KeywordsV3(marketplace)
        self._client_targets = TargetsV3(marketplace)
        self._client_negative_keywords = NegativeKeywordsV3(marketplace)
        self._client_negative_targets = NegativeTargetsV3(marketplace)
        self._report_client = Reports(marketplace)

    def list_all_entities(self, request_func, payload_name):
        l = []
        make_request = True
        next_token = None
        while make_request:
            if next_token:
                body = {'nextToken': next_token}
            else:
                body = {}
            payload = request_func(body=body).payload
            l.extend(payload.get(payload_name))
            next_token = payload.get('nextToken')
            if next_token is None:
                make_request = False
        return pd.DataFrame(l)

    def list_negative_targets(self):
        return self.list_all_entities(self._client_negative_targets.list_negative_product_targets, 'negativeTargetingClauses')

    def list_negative_keywords(self):
        return self.list_all_entities(self._client_negative_keywords.list_negative_keywords, 'negativeKeywords')

    def list_campaigns(self):
        return self.list_all_entities(self._client_campaigns.list_campaigns, 'campaigns')

    def list_keywords(self):
        return self.list_all_entities(self._client_keywords.list_keywords, 'keywords')

    def list_targets(self):
        return self.list_all_entities(self._client_targets.list_product_targets, 'targetingClauses')

    def _get_report_v3_params_targeting(self, date=None):
        date_str = self._get_date_str_v3(date)
        body = {
            "name": "SP targeting report - " + date_str,
            "startDate": date_str,
            "endDate": date_str,
            "configuration": {
                "adProduct": "SPONSORED_PRODUCTS",
                "groupBy": ["targeting"],
                "columns": ['campaignId', 'targeting', 'keywordId', 'impressions', 'clicks', 'cost', 'sales14d', 'unitsSoldClicks14d', 'attributedSalesSameSku14d', 'unitsSoldSameSku14d',],
                # "columns": ['impressions', 'clicks', 'costPerClick', 'clickThroughRate', 'cost', 'purchases1d', 'purchases7d', 'purchases14d', 'purchases30d', 'purchasesSameSku1d', 'purchasesSameSku7d', 'purchasesSameSku14d', 'purchasesSameSku30d', 'unitsSoldClicks1d', 'unitsSoldClicks7d', 'unitsSoldClicks14d', 'unitsSoldClicks30d', 'sales1d', 'sales7d', 'sales14d', 'sales30d', 'attributedSalesSameSku1d', 'attributedSalesSameSku7d', 'attributedSalesSameSku14d', 'attributedSalesSameSku30d', 'unitsSoldSameSku1d', 'unitsSoldSameSku7d', 'unitsSoldSameSku14d', 'unitsSoldSameSku30d', 'kindleEditionNormalizedPagesRead14d', 'kindleEditionNormalizedPagesRoyalties14d', 'salesOtherSku7d', 'unitsSoldOtherSku7d', 'acosClicks7d', 'acosClicks14d', 'roasClicks7d', 'roasClicks14d', 'keywordId', 'keyword', 'campaignBudgetCurrencyCode', 'startDate', 'endDate', 'portfolioId', 'campaignName', 'campaignId', 'campaignBudgetType', 'campaignBudgetAmount', 'campaignStatus', 'keywordBid', 'adGroupName', 'adGroupId', 'keywordType', 'matchType', 'targeting', 'topOfSearchImpressionShare',],
                "reportTypeId": "spTargeting",
                "timeUnit": "SUMMARY",
                "format": "GZIP_JSON"
            }
        }
        return body

    def get_report_v3_targeting(self, date=None):
        return self._get_report_v3_data(body=self._get_report_v3_params_targeting(date), report_client=self._report_client)

    def post_report_v3_targeting(self, date=None):
        return self._post_report_v3(body=self._get_report_v3_params_targeting(date), report_client=self._report_client)

    def _get_report_v3_params_searchterm(self, date):
        date_str = self._get_date_str_v3(date)
        body = {
            "name": "SP search term report - " + date_str,
            "startDate": date_str,
            "endDate": date_str,
            "configuration": {
                "adProduct": "SPONSORED_PRODUCTS",
                "groupBy": ["searchTerm"],
                'columns': ['campaignId', 'searchTerm', 'impressions', 'clicks', 'cost', 'sales14d', 'unitsSoldClicks14d', 'attributedSalesSameSku14d', 'unitsSoldSameSku14d',],
                "reportTypeId": "spSearchTerm",
                "timeUnit": "SUMMARY",
                "format": "GZIP_JSON"
            }
        }
        return body

    def get_report_v3_data_searchterm(self, date=None):
        return self._get_report_v3_data(body=self._get_report_v3_params_searchterm(date), report_client=self._report_client)

    def post_report_v3_searchterm(self, date=None):
        return self._post_report_v3(body=self._get_report_v3_params_searchterm(date), report_client=self._report_client)

    def get_report_v3_from_id(self, report_id):
        return self._get_report_v3_from_id(report_id, report_client=self._report_client)