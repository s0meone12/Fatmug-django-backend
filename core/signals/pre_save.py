from django.db.models.signals import pre_save
from django.dispatch import receiver
from core.models import AmzAdsPerformanceRptUpdate


@receiver(pre_save)
def global_pre_save(sender, instance, **kwargs):
    pass
