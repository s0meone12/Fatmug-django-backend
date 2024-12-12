from ..base import BaseTgtOpt
from .... import SBDiscProTgt
from django.db import models
from core.manager import SbProTgtOptManager


class SbProTgtOpt(BaseTgtOpt):
    disc_tgt = models.ForeignKey(SBDiscProTgt, on_delete=models.DO_NOTHING, null=True)
    manager = SbProTgtOptManager()

    class Meta:
        unique_together = ('disc_tgt', 'date', 'opt_duration')