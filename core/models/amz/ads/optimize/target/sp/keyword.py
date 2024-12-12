from ..base import BaseTgtOpt
from .... import SPDiscKeyTgt
from django.db import models
from core.manager import SpKeyTgtOptManager


class SpKeyTgtOpt(BaseTgtOpt):
    disc_tgt = models.ForeignKey(SPDiscKeyTgt, on_delete=models.DO_NOTHING, null=True)
    manager = SpKeyTgtOptManager()

    class Meta:
        unique_together = ('disc_tgt', 'date', 'opt_duration')
