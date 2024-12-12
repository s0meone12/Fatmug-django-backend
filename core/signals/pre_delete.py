from django.db.models.signals import pre_delete
from django.dispatch import receiver
# from core.models import AmzAdsPerformanceRptUpdate, Task


@receiver(pre_delete)
def global_pre_delete(sender, instance, **kwargs):
    pass