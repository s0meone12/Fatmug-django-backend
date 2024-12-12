from django.db import models
from django.db.models import Manager


class BaseModel(models.Model):
    id = models.BigAutoField(primary_key=True)
    objects = Manager()

    class Meta:
        abstract = True
