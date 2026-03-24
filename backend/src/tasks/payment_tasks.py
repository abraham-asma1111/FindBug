"""
Payment background tasks (Payouts, reconciliation)
"""
from src.tasks.celery_app import celery_app
from src.core.logging import get_logger
from src.core.constants import QUEUE_PAYMENT
from src.tasks.email_tasks import get_task_db
from src.services.payout_service import PayoutService

logger = get_logger(__name__)


@celery_app.task(name="process_payout_task", queue=QUEUE_PAYMENT, bind=True, max_retries=5)
def process_payout_task(self, payout_id: str):
    """Process a researcher payout request via Chapa/Telebirr."""
    try:
        with get_task_db() as db:
            service = PayoutService(db)
            result = service.process_payout(payout_id)
            logger.info("Payout processed", extra={"payout_id": payout_id, "result": result})
    except Exception as exc:
        logger.error(f"Failed to process payout: {exc}", extra={"payout_id": payout_id})
        # Exponential backoff
        raise self.retry(exc=exc, countdown=2 ** self.request.retries * 60)


@celery_app.task(name="reconcile_payments_task", queue=QUEUE_PAYMENT)
def reconcile_payments_task():
    """Daily reconciliation of pending payments and balances."""
    try:
        with get_task_db() as db:
            service = PayoutService(db)
            # Find stuck pending payments and verify status with gateway
            count = service.reconcile_all_pending()
            logger.info("Payment reconciliation complete", extra={"reconciled_count": count})
    except Exception as exc:
        logger.error(f"Failed to reconcile payments: {exc}")
