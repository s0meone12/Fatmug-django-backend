from ....inheritance import BaseModel
from django.db import models


class BaseAction(BaseModel):
    state = models.CharField(max_length=255, blank=False, null=False, default="draft", choices=(
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('error', 'Error'),
    ))
    message = models.TextField(null=True, blank=True, default="")
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        abstract = True
