"""
Celery application — async task queue backed by Redis.
"""
from celery import Celery
from backend.core.config import settings

celery_app = Celery(
    "cloudgrc",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["backend.workers.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_routes={
        "backend.workers.tasks.run_scan_task": {"queue": "scans"},
        "backend.workers.tasks.send_report_email": {"queue": "emails"},
    },
)
