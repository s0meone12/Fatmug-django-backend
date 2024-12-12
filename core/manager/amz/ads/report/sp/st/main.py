from ......base import BaseManager
import pandas as pd


class SpStReportManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__amz_sku = None
        self.__rpt_update = None

    @property
    def amz_sku(self):
        if self.__amz_sku is None:
            from .amz_sku import AmzSkuSubManagerSpStReport
            self.__amz_sku = AmzSkuSubManagerSpStReport(self)
        return self.__amz_sku

    @property
    def rpt_update(self):
        from .rpt_update import AmzAdsPerformanceRptUpdateSubManagerSpStReport
        if self.__rpt_update is None:
            self.__rpt_update = AmzAdsPerformanceRptUpdateSubManagerSpStReport(
                self)
        return self.__rpt_update

    
