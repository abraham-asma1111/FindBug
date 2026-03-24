"""
Notification background tasks
"""
from src.tasks.celery_app import celery_app
from src.core.logging import get_logger
from src.core.constants import QUEUE_NOTIFICATION
from src.tasks.email_tasks import get_task_db
from src.services.notification_service import NotificationService

logger = get_logger(__name__)


@celery_app.task(name="send_notification_task", queue=QUEUE_NOTIFICATION, bind=True, max_retries=3)
def send_notification_task(self, user_id: str, title: str, message: str, notification_type: str):
    """"""
    try:
        with get_task_db() as db:
            service = NotificationService(db)
            service.create_notification(
                user_id=user_id,
                title=title,
                message=message,
                notification_type=notification_type
            )
            logger.info("Notification sent", extra={"user_id": user_id, "type": notification_type})
    except Exception as exc:
        logger.error(f"Failed to send notification: {exc}", extra={"user_id": user_id})
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(name="broadcast_notification_task", queue=QUEUE_NOTIFICATION, bind=True)
def broadcast_notification_task(self, title: str, message: str, role: str = None):
    """"""
    try:
        with get_task_db() as db:
            service = NotificationService(db)
            service.broadcast(title=title, message=message, role=role)
            logger.info("Broadcast notification sent", extra={"role": role})
    except Exception as exc:
        logger.error(f"Failed to broadcast notification: {exc}")
        raise self.retry(exc=exc, countdown=120)
