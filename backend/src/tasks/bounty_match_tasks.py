"""
Bounty Match background tasks
"""
from src.tasks.celery_app import celery_app
from src.core.logging import get_logger
from src.core.constants import QUEUE_MATCHING
from src.tasks.email_tasks import get_task_db
from src.services.matching_service import MatchingService

logger = get_logger(__name__)


@celery_app.task(name="recompute_researcher_scores_task", queue=QUEUE_MATCHING)
def recompute_researcher_scores_task():
    """Background job to recompute researcher match scores."""
    try:
        with get_task_db() as db:
            service = MatchingService(db)
            service.recompute_all()
            logger.info("Researcher match scores recomputed successfully.")
    except Exception as exc:
        logger.error(f"Failed to recompute scores: {exc}")


@celery_app.task(name="refresh_match_cache_task", queue=QUEUE_MATCHING)
def refresh_match_cache_task():
    """Nightly cache refresh for fast matching lookups."""
    try:
        with get_task_db() as db:
            service = MatchingService(db)
            service.refresh_cache()
            logger.info("Match cache refreshed successfully.")
    except Exception as exc:
        logger.error(f"Failed to refresh match cache: {exc}")
