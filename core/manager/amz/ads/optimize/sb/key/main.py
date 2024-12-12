from ......base import BaseManager


class SbKeyTgtOptManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__associated_report = None
        self.__disc_tgt = None

    @property
    def disc_tgt(self):
        if self.__disc_tgt is None:
            from .disc_tgt import SBDiscKeyTgtSubManagerSbKeyTgtOpt
            self.__disc_tgt = SBDiscKeyTgtSubManagerSbKeyTgtOpt(self)
        return self.__disc_tgt

    @property
    def associated_report(self):
        if self.__associated_report is None:
            from .sb_st_rpt import SbStReportSubManagerSbKeyTgtOpt
            self.__associated_report = SbStReportSubManagerSbKeyTgtOpt(self)
        return self.__associated_report
   
