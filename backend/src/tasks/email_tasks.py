"""
Email background tasks
"""
from src.tasks.celery_app import celery_app
from src.core.email_service import EmailService
from src.core.logging import get_logger
from src.core.constants import QUEUE_EMAIL

logger = get_logger(__name__)

# To use DB inside tasks, we get a short-lived session context
from contextlib import contextmanager
from src.core.database import SessionLocal

@contextmanager
def get_task_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@celery_app.task(name="send_verification_email_task", queue=QUEUE_EMAIL, bind=True, max_retries=3)
def send_verification_email_task(self, email: str, token: str):
    try:
        with get_task_db() as db:
            service = EmailService(db)
            service.send_verification_email(email, token)
            logger.info("Verification email sent", extra={"email": email})
    except Exception as exc:
        logger.error(f"Failed to send verification email: {exc}", extra={"email": email})
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(name="send_password_reset_task", queue=QUEUE_EMAIL, bind=True, max_retries=3)
def send_password_reset_task(self, email: str, token: str):
    try:
        with get_task_db() as db:
            service = EmailService(db)
            service.send_password_reset_email(email, token)
            logger.info("Password reset email sent", extra={"email": email})
    except Exception as exc:
        logger.error(f"Failed to send password reset email: {exc}", extra={"email": email})
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(name="send_bounty_awarded_task", queue=QUEUE_EMAIL, bind=True, max_retries=3)
def send_bounty_awarded_task(self, email: str, amount: float, program_name: str, currency: str = "ETB"):
    try:
        with get_task_db() as db:
            service = EmailService(db)
            # Assuming a generic template sender or similar method exists
            service.send_email(
                to_email=email,
                subject=f"🏆 Bounty Awarded: {currency} {amount:,.2f} from {program_name}!",
                body=f"Congratulations! You've been awarded {currency} {amount:,.2f} for your valid find in {program_name}."
            )
            logger.info("Bounty awarded email sent", extra={"email": email, "amount": amount})
    except Exception as exc:
        logger.error(f"Failed to send bounty awarded email: {exc}", extra={"email": email})
        raise self.retry(exc=exc, countdown=60)
