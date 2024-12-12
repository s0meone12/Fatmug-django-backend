from ..base import BaseTgtOpt
from django.db import models
from .... import SBDiscKeyTgt
from core.manager import SbKeyTgtOptManager


class SbKeyTgtOpt(BaseTgtOpt):
    disc_tgt = models.ForeignKey(SBDiscKeyTgt, on_delete=models.DO_NOTHING, null=True)
    manager = SbKeyTgtOptManager()

    class Meta:
        unique_together = ('disc_tgt', 'date', 'opt_duration')