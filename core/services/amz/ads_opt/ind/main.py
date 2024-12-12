from .aggregate import AmzAdsOptIndAggregate
from .associate_after_publs import AmzAdsIndAssociateLiveToDisc
from .discover.main import AmzInAdsDiscoveryDataAggregator
from .optimize import AmzAdsIndOptimize
from .action import AmzAdsIndActionGenerator
from .publish import AmzAdsIndPublish


class AmzInAdsOptimizor:
    def __init__(self):
        self.__agg = AmzAdsOptIndAggregate()
        self.__aso = AmzAdsIndAssociateLiveToDisc()
        self.__dis = AmzInAdsDiscoveryDataAggregator()
        self.__opt = AmzAdsIndOptimize()
        self.__act = AmzAdsIndActionGenerator()
        self.__pub = AmzAdsIndPublish()

    def run(self):
        self.__agg._run()
        self.__aso._run()
        self.__dis._run()
        self.__opt._run()
        self.__act._run()
        # self.__pub._run()
