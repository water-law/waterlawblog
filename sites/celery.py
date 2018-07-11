import os
from datetime import timedelta
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sites.settings')

from django.conf import settings as django_settings


class Config:
    BROKER_URL = django_settings.REDIS_CONNECTION
    CELERY_RESULT_BACKEND = django_settings.REDIS_CONNECTION
    CELERY_TIMEZONE = django_settings.TIME_ZONE
    CELERY_ENABLE_UTC = True
    # CELERYBEAT_SCHEDULE = {
    #     "reset_draw": {
    #         "task": "racket.tasks.reset_draw",
    #         "schedule": crontab(hour=0, minute=1),
    #     },
    # }

    CELERY_ACCEPT_CONTENT = ['pickle', "json"]
    CELERYBEAT_MAX_LOOP_INTERVAL = 1


app = Celery('sites')
app.config_from_object(Config)

app.autodiscover_tasks(lambda: django_settings.INSTALLED_APPS)
