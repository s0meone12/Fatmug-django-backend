from django.core.management.base import BaseCommand
from core.models import AmzSku


class Command(BaseCommand):
    help = 'Load live models data in discovered models, before run discovery load live data in Discovered model, one time.'

    def handle(self, *args, **options):
        AmzSku.manager.ads_opt.run()
