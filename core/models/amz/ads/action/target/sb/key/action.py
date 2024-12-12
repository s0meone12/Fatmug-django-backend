from django.db import models
from ..... import SBDiscKeyTgt
from ....base import BaseAction
from core.manager import SbKeyTargActionManager


class SbKeyTgtAction(BaseAction):
    disc_target = models.ForeignKey(
        SBDiscKeyTgt, on_delete=models.RESTRICT, null=False, blank=False)
    manager= SbKeyTargActionManager()
