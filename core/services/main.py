from .amz.ads_opt.main import AmzAdsOptimizor
from .amz.main import AmzService


class Service:
    def __init__(self):
        self.amz = AmzService()


srv = Service()
