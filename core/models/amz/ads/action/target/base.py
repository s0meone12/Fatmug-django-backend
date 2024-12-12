from .....inheritance import BaseModel
from django.db import models


class BaseTgtActionValues(BaseModel):
    old_value = models.CharField(max_length=255, null=True, blank=True)
    new_value = models.CharField(max_length=255, null=False, blank=False)

    class Meta:
        abstract = True