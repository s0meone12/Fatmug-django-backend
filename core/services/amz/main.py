from .sku_repricer import AmzSkuRepricer


class AmzService:
    def __init__(self):
        self.sku_repricer = AmzSkuRepricer()

