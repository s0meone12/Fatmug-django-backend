from django.db.models.signals import post_migrate
from django.dispatch import receiver
# from core.models import Task



@receiver(post_migrate)
def global_post_migrate(sender, **kwargs):
    pass
