from django.db.models.signals import post_save
from django.dispatch import receiver
# from core.models import Task
from core.celery.config import app as celery


@receiver(post_save)
def global_post_save(sender, instance, created, **kwargs):
    pass
