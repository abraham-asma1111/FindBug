"""
Celery App Initialization
Sets up the background task runner and periodic task schedule for FindBug Platform
"""
import os
from celery import Celery

from src.core.config import settings
from src.core.constants import BEAT_SCHEDULE


# Initialize Celery app
celery_app = Celery(
    "findbug_tasks",
    broker=str(settings.CELERY_BROKER_URL) if hasattr(settings, "CELERY_BROKER_URL") else "redis://localhost:6379/1",
    backend=str(settings.CELERY_RESULT_BACKEND) if hasattr(settings, "CELERY_RESULT_BACKEND") else "redis://localhost:6379/2"
)


# Configuration tuning
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Retry configuration
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    
    # Task time limits
    task_soft_time_limit=300,  # 5 minutes
    task_time_limit=360,       # Killed at 6 minutes
    
    # Beat schedule
    beat_schedule=BEAT_SCHEDULE,
)

# Auto-discover tasks in the tasks module
celery_app.autodiscover_tasks(["src.tasks"], related_name=None, force=True)

# For running tasks synchronously during unit tests if CELERY_TASK_ALWAYS_EAGER is True
if os.environ.get("CELERY_TASK_ALWAYS_EAGER", "False").lower() == "true":
    celery_app.conf.update(task_always_eager=True)
