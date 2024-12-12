from django.shortcuts import render
from django.http import HttpResponse
from core.models import *
from core.services.amz.sell import AmzSellService
from core.apis.clients.amz.ads.fetcher import AmzAdsSbFetcher, AmzAdsSdFetcher, AmzAdsSpFetcher
from core.services.amz.ads_opt.ind.main import *


def testing(request):
    def update_bid_back_to_live():
        df = pd.DataFrame(SBDiscKeyTgt.manager.filter(keyword__isnull=False).values('id','keyword__bid'))
        df.rename(columns={'keyword__bid':'bid'},inplace=True)
        df['bid'] = df['bid'].fillna(0)
        SBDiscKeyTgt.manager.dfdb.sync(df)
        df = pd.DataFrame(SBDiscProTgt.manager.filter(target__isnull=False).values('id','target__bid'))
        df.rename(columns={'target__bid':'bid'},inplace=True)
        df['bid'] = df['bid'].fillna(0)
        SBDiscProTgt.manager.dfdb.sync(df)
        df = pd.DataFrame(SPDiscKeyTgt.manager.filter(keyword__isnull=False).values('id','keyword__bid'))
        df.rename(columns={'keyword__bid':'bid'},inplace=True)
        df['bid'] = df['bid'].fillna(0)
        SPDiscKeyTgt.manager.dfdb.sync(df)
        df = pd.DataFrame(SPDiscProTgt.manager.filter(target__isnull=False).values('id','target__bid'))
        df.rename(columns={'target__bid':'bid'},inplace=True)
        df['bid'] = df['bid'].fillna(0)
        SPDiscProTgt.manager.dfdb.sync(df)
        
    # update_bid_back_to_live()

    # a=SbKeyTgtOpt.manager.disc_tgt.set_max_bid()
    # b=SbKeyTgtOpt.manager.disc_tgt.set_muted_on_unviable_and_optimize_bid()
    # c=SbKeyTgtOpt.manager.disc_tgt.optimize_bid_with_no_spend()
    # r=a+b+c
    # x=SbKeyTgtOpt.manager.filter(keyword__isnull=False).count()
    # print(x)
    # print(f'{a}=a, {b}=b, {c}=c, ==> a+b+c=r={r}, {x}=x')

    # t = AmzAdsIndOptimize()
    # t._run()
    SbKeyTgtOpt.manager.disc_tgt.set_max_bid()
    SbKeyTgtOpt.manager.disc_tgt.set_muted_on_unviable_and_optimize_bid()
    SbKeyTgtOpt.manager.disc_tgt.optimize_bid_with_no_spend()


    # di = AmzInAdsDiscoveryDataAggregator()
    # di._run()

    
    return HttpResponse("Testing...!")