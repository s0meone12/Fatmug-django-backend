from ......base import BaseManager

class SpKeyTgtOptManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__associated_report= None
        self.__disc_tgt = None

    @property
    def disc_tgt(self):
        if self.__disc_tgt is None:
            from .disc_tgt import SPDiscKeyTgtSubManagerSpKeyTgtOpt
            self.__disc_tgt = SPDiscKeyTgtSubManagerSpKeyTgtOpt(self)
        return self.__disc_tgt

    @property
    def associated_report(self):
        if self.__associated_report is None:
            from .sp_tgt_rpt import SpTgtReportSubManagerSpKeyTgtOpt
            self.__associated_report = SpTgtReportSubManagerSpKeyTgtOpt(self)
        return self.__associated_report
