"""
Analytics and Leaderboard background tasks
"""
from src.tasks.celery_app import celery_app
from src.core.logging import get_logger
from src.core.constants import QUEUE_ANALYTICS
from src.tasks.email_tasks import get_task_db
from src.services.analytics_service import AnalyticsService

logger = get_logger(__name__)


@celery_app.task(name="aggregate_daily_stats_task", queue=QUEUE_ANALYTICS)
def aggregate_daily_stats_task():
    """Aggregates daily statistics for platform, researchers, and organizations."""
    try:
        with get_task_db() as db:
            service = AnalyticsService(db)
            service.aggregate_daily_stats()
            logger.info("Daily platform stats aggregated successfully.")
    except Exception as exc:
        logger.error(f"Failed to aggregate daily stats: {exc}")


@celery_app.task(name="generate_leaderboard_task", queue=QUEUE_ANALYTICS)
def generate_leaderboard_task():
    """Recalculates global researcher leaderboard rankings."""
    try:
        with get_task_db() as db:
            service = AnalyticsService(db)
            service.generate_leaderboards()
            logger.info("Leaderboards updated successfully.")
    except Exception as exc:
        logger.error(f"Failed to generate leaderboards: {exc}")
