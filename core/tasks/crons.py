from __future__ import absolute_import, unicode_literals
from core.celery.config import app as celery
from core.models import AmzSku


@celery.task(name='sample_task')
def sample_task():
    print('Sample task executed!')


@celery.task(name='reprice_amz_sku')
def reprice_amz_sku():
    AmzSku.manager.cron.reprice()
