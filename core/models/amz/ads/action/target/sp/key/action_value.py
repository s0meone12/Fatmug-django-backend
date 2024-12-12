from ...base import BaseTgtActionValues
from core.manager import SpKeyTargActionValueManager
from .action import SpKeyTgtAction
from django.db import models


class SpKeyTgtActionValues(BaseTgtActionValues):
    action = models.ForeignKey(
        SpKeyTgtAction, on_delete=models.RESTRICT, null=False, blank=False, unique=True)
    manager = SpKeyTargActionValueManager()
