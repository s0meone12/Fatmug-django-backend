from django.db import models
from ...base import BaseTgtActionValues
from core.manager import SbKeyTargActionValueManager
from .action import SbKeyTgtAction


class SbKeyTgtActionValues(BaseTgtActionValues):
    action = models.ForeignKey(
        SbKeyTgtAction, on_delete=models.RESTRICT, null=False, blank=False, unique=True)
    manager = SbKeyTargActionValueManager()
