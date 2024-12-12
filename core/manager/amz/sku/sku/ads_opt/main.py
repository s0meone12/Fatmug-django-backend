class AdsOptSubManagerAmzSku:

    def __init__(self, manager):
        self.manager = manager
        self.__aso = None
        self.__agg = None
        self.__dis = None

    @property
    def aso(self):
        if self.__aso is None:
            from .aso import AdsAssociationSubManagerAmzSku
            self.__aso = AdsAssociationSubManagerAmzSku(self)
        return self.__aso

    @property
    def agg(self):
        if self.__agg is None:
            from .agg import AdsDataAggregationSubManagerAmzSku
            self.__agg = AdsDataAggregationSubManagerAmzSku(self.manager)
        return self.__agg

    @property
    def dis(self):
        if self.__dis is None:
            from .dis import AdsDiscoverySubManagerAmzSku
            self.__dis = AdsDiscoverySubManagerAmzSku(self.manager)
        return self.__dis

    def run(self):
        # self.agg._run()
        self.aso._run()
