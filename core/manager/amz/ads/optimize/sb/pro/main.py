from ......base import BaseManager


class SbProTgtOptManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__associated_report = None
        self.__disc_tgt = None

    @property
    def disc_tgt(self):
        if self.__disc_tgt is None:
            from .disc_tgt import SBDiscProTgtSubManagerSbProTgtOpt
            self.__disc_tgt = SBDiscProTgtSubManagerSbProTgtOpt(self)
        return self.__disc_tgt
    
    @property
    def associated_report(self):
        if self.__associated_report is None:
            from .sb_tgt_rpt import SbTgtReportSubManagerSbProTgtOpt
            self.__associated_report = SbTgtReportSubManagerSbProTgtOpt(self)
        return self.__associated_report
