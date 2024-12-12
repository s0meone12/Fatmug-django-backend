from .base import AmzAdsBaseFetcher
import json,time,os,pandas as pd
from kn_api._kn_ad_api.sd import Campaigns, Targets, Reports, NegativeTargets, Reports
from sp_api.base import Marketplaces


class AmzAdsSdFetcher(AmzAdsBaseFetcher):

    def __init__(self,marketplace: Marketplaces, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._client_campaigns = Campaigns(marketplace)
        self._client_targets = Targets(marketplace)
        self._report_client = Reports(marketplace)
        self._client_negative_targets = NegativeTargets(marketplace)

    def list_negative_targets(self):
        l = []
        make_request = True
        i = 0
        page_szie = 5000
        while make_request:
            payload = self._client_negative_targets.list_negative_targets(**{
                'startIndex': i,
                'count': page_szie,
                'stateFilter': 'enabled,paused,archived',
            }).payload
            if payload:
                l.extend(payload)
                i += page_szie
            else:
                make_request = False
        return pd.DataFrame(l)

    def list_campaigns(self):
        l = []
        make_request = True
        i = 0
        page_szie = 5000
        while make_request:
            payload = self._client_campaigns.list_campaigns(**{
                'startIndex': i,
                'count': page_szie,
                'stateFilter': 'enabled,paused,archived',
            }).payload
            if payload:
                l.extend(payload)
                i += page_szie
            else:
                make_request = False
        return pd.DataFrame(l)

    def list_targets(self):
        l = []
        make_request = True
        i = 0
        page_szie = 5000
        while make_request:
            payload = self._client_targets.list_products_targets(**{
                'startIndex': i,
                'count': page_szie,
            }).payload
            if payload:
                l.extend(payload)
                i += page_szie
            else:
                make_request = False
        return pd.DataFrame(l)

    # Sponsored Display - Matched Target

    def _get_report_v2_params_ct_matched_target(self, date):
        date_str = self._get_date_str_v2(date)
        body = {
            "reportDate": date_str,
            "tactic": "T00020",
            "metrics": "adGroupId,adGroupName,attributedConversions14d,attributedConversions14dSameSKU,attributedConversions1d,attributedConversions1dSameSKU,attributedConversions30d,attributedConversions30dSameSKU,attributedConversions7d,attributedConversions7dSameSKU,attributedDetailPageView14d,attributedOrdersNewToBrand14d,attributedSales14d,attributedSales14dSameSKU,attributedSales1d,attributedSales1dSameSKU,attributedSales30d,attributedSales30dSameSKU,attributedSales7d,attributedSales7dSameSKU,attributedSalesNewToBrand14d,attributedUnitsOrdered14d,attributedUnitsOrdered1d,attributedUnitsOrdered30d,attributedUnitsOrdered7d,attributedUnitsOrderedNewToBrand14d,campaignId,campaignName,clicks,cost,currency,impressions,targetId,targetingExpression,targetingText,targetingType,viewAttributedConversions14d,viewAttributedDetailPageView14d,viewAttributedSales14d,viewAttributedUnitsOrdered14d,viewAttributedOrdersNewToBrand14d,viewAttributedSalesNewToBrand14d,viewAttributedUnitsOrderedNewToBrand14d,attributedBrandedSearches14d,viewAttributedBrandedSearches14d",
            # "metrics": "campaignId,targetId,impressions,clicks,cost,attributedSales14d,attributedUnitsOrdered14d",
            "segment": "matchedTarget"
        }
        return body

    def get_report_v2_data_ct_matched_target(self, date=None):
        return self._get_report_v2_data(recordType='targets', body=self._get_report_v2_params_ct_matched_target(date))

    def post_report_v2_ct_matched_target(self, date=None):
        return self._post_report_v2(recordType='targets', body=self._get_report_v2_params_ct_matched_target(date), report_client=self._report_client)

    def _get_report_v2_params_at_matched_target(self, date):
        date_str = self._get_date_str_v2(date)
        body = {
            "reportDate": date_str,
            "tactic": "T00030",
            "metrics": "adGroupId,adGroupName,attributedConversions14d,attributedConversions14dSameSKU,attributedConversions1d,attributedConversions1dSameSKU,attributedConversions30d,attributedConversions30dSameSKU,attributedConversions7d,attributedConversions7dSameSKU,attributedDetailPageView14d,attributedOrdersNewToBrand14d,attributedSales14d,attributedSales14dSameSKU,attributedSales1d,attributedSales1dSameSKU,attributedSales30d,attributedSales30dSameSKU,attributedSales7d,attributedSales7dSameSKU,attributedSalesNewToBrand14d,attributedUnitsOrdered14d,attributedUnitsOrdered1d,attributedUnitsOrdered30d,attributedUnitsOrdered7d,attributedUnitsOrderedNewToBrand14d,campaignId,campaignName,clicks,cost,currency,impressions,targetId,targetingExpression,targetingText,targetingType,viewAttributedConversions14d,viewAttributedDetailPageView14d,viewAttributedSales14d,viewAttributedUnitsOrdered14d,viewAttributedOrdersNewToBrand14d,viewAttributedSalesNewToBrand14d,viewAttributedUnitsOrderedNewToBrand14d,attributedBrandedSearches14d,viewAttributedBrandedSearches14d",
            # "metrics": "campaignId,targetId,impressions,clicks,cost,attributedSales14d,attributedUnitsOrdered14d",
            "segment": "matchedTarget"
        }
        return body

    def get_report_v2_data_at_matched_target(self, date=None):
        return self._get_report_v2_data(recordType='targets', body=self._get_report_v2_params_at_matched_target(date))

    def post_report_v2_at_matched_target(self, date=None):
        return self._post_report_v2(recordType='targets', body=self._get_report_v2_params_at_matched_target(date), report_client=self._report_client)

    def get_report_v2_from_id(self, report_id):
        return self._get_report_v2_from_id(report_id, report_client=self._report_client)