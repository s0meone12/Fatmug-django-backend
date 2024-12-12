from .aggregate import AmzSkuRepricerAggregator
class AmzSkuRepricer:
    def __init__(self):
        self.agg = AmzSkuRepricerAggregator
        self.pri = None
        self.__act = None
        self.__pub = None

    def run(self):
        AmzSkuRepricerAggregator.run()
