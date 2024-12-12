import time, json
from .base import AmzAdsBaseFetcher
import pandas as pd
from kn_api._kn_ad_api.sb import CampaignsV4, Keywords, Targets, NegativeTargets, NegativeKeywords, Reports
from sp_api.base import Marketplaces


class AmzAdsSbFetcher(AmzAdsBaseFetcher):
    def __init__(self,marketplace: Marketplaces ,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self._client_campaigns = CampaignsV4(marketplace)
        self._client_keywords = Keywords(marketplace)
        self._client_targets = Targets(marketplace)
        self._client_negative_targets = NegativeTargets(marketplace)
        self._client_negative_keywords = NegativeKeywords(marketplace)
        self._report_client = Reports(marketplace)

    def list_negative_targets(self):
        l = []
        make_request = True
        next_token = None
        while make_request:
            if next_token:
                body = {'nextToken': next_token, }
            else:
                body = {}
            payload = self._client_negative_targets.list_negative_targets(
                body=body).payload
            l.extend(payload.get('negativeTargets'))
            next_token = payload.get('nextToken')
            if next_token is None:
                make_request = False
        return pd.DataFrame(l)

    def list_negative_keywords(self):
        l = []
        make_request = True
        i = 0
        page_szie = 5000
        while make_request:
            payload = self._client_negative_keywords.list_negative_keywords(**{
                'startIndex': i,
                'count': page_szie,
                'stateFilter': 'enabled,pending,archived',
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
        next_token = None
        while make_request:
            if next_token:
                body = {
                    'nextToken': next_token,
                    'stateFilter': {
                        'include': ['ENABLED', 'PAUSED', 'ARCHIVED'],
                    }}
            else:
                body = {
                    'stateFilter': {
                        'include': ['ENABLED', 'PAUSED', 'ARCHIVED'],
                    }}
            payload = self._client_campaigns.list_campaigns(
                body=body).payload
            l.extend(payload.get('campaigns'))
            next_token = payload.get('nextToken')
            if next_token is None:
                make_request = False
        return pd.DataFrame(l)

    def list_keywords(self):
        l = []
        make_request = True
        i = 0
        page_szie = 5000
        while make_request:
            payload = self._client_keywords.list_keywords(**{
                'startIndex': i,
                'count': page_szie,
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
        next_token = None
        while make_request:
            # import ipdb; ipdb.set_trace(); 
            if next_token:
                body = {
                    "nextToken": next_token
                    }
            else:
                body = {}
            body_json_dump = json.dumps(body)
            response = self._client_targets.list_products_targets(
                body=body_json_dump)
            payload = response.payload
            l.extend(payload.get('targets'))
            next_token = payload.get("nextToken")
            if next_token is None:
                make_request = False
        return pd.DataFrame(l)

    def _get_report_v2_params_searchterm(self, date=None):
        date_str = self._get_date_str_v2(date)
        body = {
            'reportDate': date_str,
            'creativeType': 'all',
            # 'metrics': 'adGroupId,adGroupName,attributedConversions14d,attributedSales14d,campaignBudget,campaignBudgetType,campaignStatus,clicks,cost,impressions,keywordBid,keywordId,keywordStatus,keywordText,matchType,vctr,video5SecondViewRate,video5SecondViews,videoCompleteViews,videoFirstQuartileViews,videoMidpointViews,videoThirdQuartileViews,videoUnmutes,viewableImpressions,vtr,currency'
            'metrics': 'campaignId,keywordId,impressions,clicks,cost,attributedSales14d'
        }
        return body

    def post_report_v2_searchterm(self, date=None):
        return self._post_report_v2(recordType='keywords', body=self._get_report_v2_params_searchterm(date), report_client=self._report_client)

    def get_report_v2_data_searchterm(self, date=None):
        return self._get_report_v2_data(recordType='keywords', body=self._get_report_v2_params_searchterm(date))

    def _get_report_v2_params_targeting(self, date=None):
        date_str = self._get_date_str_v2(date)
        body = {
            'reportDate': date_str,
            'creativeType': 'all',
            # 'metrics': 'adGroupId,adGroupName,attributedConversions14d,attributedConversions14dSameSKU,attributedSales14d,attributedSales14dSameSKU,campaignBudget,campaignBudgetType,campaignId,campaignName,campaignStatus,clicks,cost,impressions,targetId,targetingExpression,targetingText,targetingType,vctr,video5SecondViewRate,video5SecondViews,videoCompleteViews,videoFirstQuartileViews,videoMidpointViews,videoThirdQuartileViews,videoUnmutes,viewableImpressions,vtr,dpv14d,attributedDetailPageViewsClicks14d,attributedOrderRateNewToBrand14d,attributedOrdersNewToBrand14d,attributedOrdersNewToBrandPercentage14d,attributedSalesNewToBrand14d,attributedSalesNewToBrandPercentage14d,attributedUnitsOrderedNewToBrand14d,attributedUnitsOrderedNewToBrandPercentage14d,attributedBrandedSearches14d,currency,topOfSearchImpressionShare'
            'metrics': 'campaignId,targetId,impressions,clicks,cost,attributedSales14d'
        }
        return body

    def post_report_v2_targeting(self, date=None):
        return self._post_report_v2(recordType='targets', body=self._get_report_v2_params_targeting(date), report_client=self._report_client)

    def get_report_v2_data_targeting(self, date=None):
        return self._get_report_v2_data(recordType='targets', body=self._get_report_v2_params_targeting(date))

    def get_report_v2_from_id(self, report_id):
        return self._get_report_v2_from_id(report_id, report_client=self._report_client)
