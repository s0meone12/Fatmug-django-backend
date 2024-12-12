from ......base import BaseManager


class SdMtReportManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__rpt_update = None

    @property
    def rpt_update(self):
        from .rpt_update import AmzAdsPerformanceRptUpdateSubManagerSdMtReport
        if self.__rpt_update is None:
            self.__rpt_update = AmzAdsPerformanceRptUpdateSubManagerSdMtReport(
                self)
        return self.__rpt_update
