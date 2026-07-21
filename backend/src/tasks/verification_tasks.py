"""Daily reverification scheduler — suspends scopes that fail ownership recheck."""
import logging
from datetime import datetime

logger = logging.getLogger("ptaas.scheduler")

_scheduler_started = False


def start_reverification_scheduler(app=None):
    """Start the APScheduler daily reverification job.

    Call this from FastAPI's startup event.  Safe to call multiple times.
    """
    global _scheduler_started
    if _scheduler_started:
        return

    try:
        from apscheduler.schedulers.background import BackgroundScheduler  # type: ignore
        from apscheduler.triggers.cron import CronTrigger  # type: ignore

        scheduler = BackgroundScheduler()
        scheduler.add_job(
            _run_daily_reverification,
            trigger=CronTrigger(hour=2, minute=0),   # 02:00 server time daily
            id="daily_reverification",
            replace_existing=True,
            misfire_grace_time=3600,
        )
        scheduler.start()
        _scheduler_started = True
        logger.info("✅ Reverification scheduler started (runs daily at 02:00)")

    except ImportError:
        logger.warning(
            "apscheduler not installed — reverification scheduler not started. "
            "Install with: pip install apscheduler"
        )
    except Exception as exc:
        logger.error(f"Failed to start reverification scheduler: {exc}")


def _run_daily_reverification():
    """Job function: open a DB session and call reverify_all()."""
    try:
        from src.core.database import SessionLocal
        from src.services.scope_verification_service import ScopeVerificationService

        db = SessionLocal()
        try:
            svc = ScopeVerificationService(db)
            results = svc.reverify_all()
            logger.info(
                f"[{datetime.utcnow().isoformat()}] Daily reverification complete: {results}"
            )
        finally:
            db.close()
    except Exception as exc:
        logger.error(f"Reverification job error: {exc}", exc_info=True)
