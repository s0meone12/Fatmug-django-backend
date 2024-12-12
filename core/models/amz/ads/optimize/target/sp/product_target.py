from ..base import BaseTgtOpt
from .... import SPDiscProTgt
from django.db import models
from core.manager import SpProTgtOptManager


class SpProTgtOpt(BaseTgtOpt):
    disc_tgt = models.ForeignKey(SPDiscProTgt, on_delete=models.DO_NOTHING, null=True)
    manager = SpProTgtOptManager()

    class Meta:
        unique_together = ('disc_tgt', 'date', 'opt_duration')