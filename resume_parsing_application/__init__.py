# make sure celery is loaded
from .celery import app as celery_app

__all__ = ("celery_app",)
