import os
import sys
from celery import Celery
from celery.schedules import crontab

parent = os.path.abspath(".")
sys.path.insert(1, parent)


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
app = Celery("config")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()