from django.db import models
from ...base import BaseTgtActionValues
from core.manager import SpProTargActionValueManager
from .action import SpProTgtAction


class SpProTgtActionValues(BaseTgtActionValues):
    action = models.ForeignKey(
        SpProTgtAction, on_delete=models.RESTRICT, null=False, blank=False, unique=True)
    manager = SpProTargActionValueManager()
