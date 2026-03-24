"""
Environment-level constants for FindBug Platform
"""
from src.utils.constants import (
    ACCESS_TOKEN_TTL,
    REFRESH_TOKEN_TTL,
    EMAIL_VERIFY_TOKEN_TTL,
    PASSWORD_RESET_TOKEN_TTL,
    MAX_FILE_SIZE_BYTES,
    MAX_LOGIN_ATTEMPTS,
    LOCKOUT_DURATION_MINUTES,
    QUEUE_EMAIL,
    QUEUE_NOTIFICATION,
    QUEUE_REPORT,
    QUEUE_PAYMENT,
    QUEUE_CLEANUP,
    QUEUE_ANALYTICS,
    QUEUE_MATCHING,
    PLATFORM_COMMISSION_RATE,
    MIN_PAYOUT_AMOUNT,
)

# Re-export for convenience of core-layer imports
__all__ = [
    "ACCESS_TOKEN_TTL",
    "REFRESH_TOKEN_TTL",
    "EMAIL_VERIFY_TOKEN_TTL",
    "PASSWORD_RESET_TOKEN_TTL",
    "MAX_FILE_SIZE_BYTES",
    "MAX_LOGIN_ATTEMPTS",
    "LOCKOUT_DURATION_MINUTES",
    "QUEUE_EMAIL",
    "QUEUE_NOTIFICATION",
    "QUEUE_REPORT",
    "QUEUE_PAYMENT",
    "QUEUE_CLEANUP",
    "QUEUE_ANALYTICS",
    "QUEUE_MATCHING",
    "PLATFORM_COMMISSION_RATE",
    "MIN_PAYOUT_AMOUNT",
]

# ─── Celery Beat Schedule ─────────────────────────────────────────────────────
# Used by celery_app.py to define periodic task schedules
BEAT_SCHEDULE = {
    "cleanup-expired-tokens-daily": {
        "task": "src.tasks.cleanup_tasks.cleanup_expired_tokens_task",
        "schedule": 86400,  # every 24 h
        "options": {"queue": QUEUE_CLEANUP},
    },
    "aggregate-daily-stats": {
        "task": "src.tasks.analytics_tasks.aggregate_daily_stats_task",
        "schedule": 86400,
        "options": {"queue": QUEUE_ANALYTICS},
    },
    "refresh-leaderboard-hourly": {
        "task": "src.tasks.analytics_tasks.generate_leaderboard_task",
        "schedule": 3600,
        "options": {"queue": QUEUE_ANALYTICS},
    },
    "recompute-researcher-scores-daily": {
        "task": "src.tasks.bounty_match_tasks.recompute_researcher_scores_task",
        "schedule": 86400,
        "options": {"queue": QUEUE_MATCHING},
    },
    "reconcile-payments-daily": {
        "task": "src.tasks.payment_tasks.reconcile_payments_task",
        "schedule": 86400,
        "options": {"queue": QUEUE_PAYMENT},
    },
}

# ─── API Version ──────────────────────────────────────────────────────────────
API_VERSION = "v1"
API_PREFIX = f"/api/{API_VERSION}"
