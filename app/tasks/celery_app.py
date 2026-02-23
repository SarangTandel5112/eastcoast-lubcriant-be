from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "ecom_worker",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=[
        "app.modules.order.order_tasks",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,           # task acknowledged after completion (safer)
    worker_prefetch_multiplier=1,  # one task at a time per worker
)
