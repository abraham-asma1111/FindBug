"""
Report background tasks (Auto triage, syncing)
"""
from src.tasks.celery_app import celery_app
from src.core.logging import get_logger
from src.core.constants import QUEUE_REPORT
from src.tasks.email_tasks import get_task_db
from src.services.triage_service import TriageService
from src.services.integration_service import IntegrationService

logger = get_logger(__name__)


@celery_app.task(name="auto_triage_report_task", queue=QUEUE_REPORT, bind=True)
def auto_triage_report_task(self, report_id: str):
    """Automatically assess and triage a new report using basic heuristics or AI."""
    try:
        with get_task_db() as db:
            service = TriageService(db)
            result = service.auto_triage(report_id)
            logger.info("Report auto-triaged", extra={"report_id": report_id, "result": result})
    except Exception as exc:
        logger.error(f"Failed to auto-triage report: {exc}", extra={"report_id": report_id})
        raise self.retry(exc=exc, countdown=300)


@celery_app.task(name="sync_report_to_jira_task", queue=QUEUE_REPORT, bind=True)
def sync_report_to_jira_task(self, report_id: str, integration_id: str):
    """Sync a vulnerability report to an external ticketing system (e.g., Jira)."""
    try:
        with get_task_db() as db:
            service = IntegrationService(db)
            service.sync_ticket(report_id, integration_id)
            logger.info("Report synced to external tracker", extra={"report_id": report_id})
    except Exception as exc:
        logger.error(f"Failed to sync report: {exc}", extra={"report_id": report_id})
        raise self.retry(exc=exc, countdown=300)
