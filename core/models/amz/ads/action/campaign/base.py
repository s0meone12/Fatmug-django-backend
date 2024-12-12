from .....inheritance import BaseModel
from django.db import models


class BaseCampActionValues(BaseModel):
    name = models.CharField(max_length=255, null=False, blank=False, choices=(
        ('campaign_name', 'Campaign_Name'),
        ('budget', 'Budget')
    ))
    old_value = models.CharField(max_length=255, null=True, blank=True)
    new_value = models.CharField(max_length=255, null=False, blank=False)

    class Meta:
        abstract = True