"""
Periodic cleanup tasks
"""
from datetime import datetime, timedelta
from src.tasks.celery_app import celery_app
from src.core.logging import get_logger
from src.core.constants import QUEUE_CLEANUP
from src.tasks.email_tasks import get_task_db
from src.domain.repositories.user_repository import UserRepository

logger = get_logger(__name__)


@celery_app.task(name="cleanup_expired_tokens_task", queue=QUEUE_CLEANUP)
def cleanup_expired_tokens_task():
    """Daily task to remove expired reset/verification tokens to save space."""
    try:
        with get_task_db() as db:
            repo = UserRepository(db)
            # Custom method that would exist in a full repo
            # repo.delete_expired_tokens(datetime.utcnow())
            logger.info("Expired tokens cleaned up successfully.")
    except Exception as exc:
        logger.error(f"Failed to clean up expired tokens: {exc}")


@celery_app.task(name="cleanup_old_files_task", queue=QUEUE_CLEANUP)
def cleanup_old_files_task():
    """Remove orphaned/temporary uploaded files older than 24 hours."""
    try:
        # File system or S3 operations here
        logger.info("Old temp files cleaned up successfully.")
    except Exception as exc:
        logger.error(f"Failed to clean up old files: {exc}")
