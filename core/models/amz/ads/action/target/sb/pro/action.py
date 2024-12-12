from django.db import models
from ..... import SBDiscProTgt
from ....base import BaseAction
from core.manager import SbProTargActionManager


class SbProTgtAction(BaseAction):
    disc_target = models.ForeignKey(
        SBDiscProTgt, on_delete=models.RESTRICT, null=False, blank=False)
    manager= SbProTargActionManager()

