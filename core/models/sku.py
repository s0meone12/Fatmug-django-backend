from django.db import models
from .inheritance import BaseModel
from core.manager import SkuManager


class Sku(BaseModel):
    name = models.CharField(max_length=100, unique=True,
                            blank=False, null=False)

    manager = SkuManager()
