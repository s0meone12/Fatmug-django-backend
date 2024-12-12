from django.db import models
from ...base import BaseTgtActionValues
from core.manager import SbProTargActionValueManager
from .action import SbProTgtAction


class SbProTgtActionValues(BaseTgtActionValues):
    action = models.ForeignKey(
        SbProTgtAction, on_delete=models.RESTRICT, null=False, blank=False, unique=True)
    manager = SbProTargActionValueManager()
