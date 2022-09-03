"""Make sure Celery is initialized along with Django."""
from .celery import app as celery_app

__all__ = ('celery_app',)
