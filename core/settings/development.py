from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    "sample_task": {
        "task": "sample_task",  # Replace with the actual path to your Celery task
        # Run once a day at midnight
        "schedule": crontab(minute="0", hour="2"),
    },
}

