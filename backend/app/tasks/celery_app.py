from __future__ import annotations

from celery import Celery

from app.core.config import get_settings

settings = get_settings()

if settings.celery_broker_url:
    broker_url = settings.celery_broker_url
    result_backend = settings.celery_result_backend or broker_url
else:
    broker_url = "memory://"
    result_backend = "cache+memory://"

celery_app = Celery(
    "automation_worker",
    broker=broker_url,
    backend=result_backend,
    include=["app.tasks.tasks"],
)

celery_app.conf.task_always_eager = (
    settings.celery_eager or not settings.celery_broker_url
)
celery_app.conf.task_eager_propagates = True
celery_app.conf.task_store_eager_result = True
celery_app.conf.broker_connection_retry_on_startup = True
