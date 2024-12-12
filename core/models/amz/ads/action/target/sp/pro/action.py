from django.db import models
from ....base import BaseAction
from ..... import SPDiscProTgt
from core.manager import SpProTargActionManager


class SpProTgtAction(BaseAction):
    disc_target = models.ForeignKey(
        SPDiscProTgt, on_delete=models.RESTRICT, null=False, blank=False)
    manager = SpProTargActionManager()
