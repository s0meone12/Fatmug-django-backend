import os
from celery.schedules import crontab

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
CSRF_TRUSTED_ORIGINS = os.environ.get('CSRF_TRUSTED_ORIGINS', '').split(',')


CELERY_BEAT_SCHEDULE = {
    "reprice_amz_sku": {
        "task": "reprice_amz_sku",  # Replace with the actual path to your Celery task
        # Run once a day at midnight
        "schedule": crontab(minute="0", hour="0"),
    },
}
