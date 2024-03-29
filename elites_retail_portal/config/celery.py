"""Celery initialization file."""

import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "elites_retail_portal.config.settings")
app = Celery("elites_retail_portal")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
