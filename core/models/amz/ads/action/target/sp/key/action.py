from ....base import BaseAction
from ..... import SPDiscKeyTgt
from core.manager import SpKeyTargActionManager
from django.db import models


class SpKeyTgtAction(BaseAction):
    disc_target = models.ForeignKey(
        SPDiscKeyTgt, on_delete=models.RESTRICT, null=False, blank=False)
    manager = SpKeyTargActionManager()
