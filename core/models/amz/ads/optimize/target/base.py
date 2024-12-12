from django.db import models
from .....inheritance import BaseModel


class BaseTgtOpt(BaseModel):
    date = models.DateField(auto_now_add=True)
    acos = models.FloatField(default=0)  # spend / sales
    opt_duration = models.IntegerField(default=15)  # 15, 180, 999999
    impressions = models.IntegerField(default=0)
    clicks = models.IntegerField(default=0)
    spend = models.FloatField(default=0)
    spend_after_mute = models.FloatField(null=True)  # Optimzation
    sales = models.FloatField(default=0)
    old_cpc = models.FloatField(null=True)  # Optimzation
    new_cpc = models.FloatField(null=True)  # Optimzation

    class Meta:
        abstract = True