"""
Structured JSON logger for FindBug Platform
"""
import logging
import json
import sys
from datetime import datetime, timezone
from typing import Any, Optional


class JsonFormatter(logging.Formatter):
    """Formats log records as a single JSON line."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        # Merge any extra fields passed via `extra=`
        for key, value in record.__dict__.items():
            if key.startswith("_") or key in {
                "name", "msg", "args", "levelname", "levelno", "pathname",
                "filename", "module", "exc_info", "exc_text", "stack_info",
                "lineno", "funcName", "created", "msecs", "relativeCreated",
                "thread", "threadName", "processName", "process", "message",
            }:
                continue
            log_entry[key] = value
        return json.dumps(log_entry, default=str)


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Return a named logger that outputs structured JSON to stdout.

    Usage:
        logger = get_logger(__name__)
        logger.info("User registered", extra={"user_id": "abc123"})
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
    logger.setLevel(level)
    logger.propagate = False
    return logger


# ─── Pre-built loggers ────────────────────────────────────────────────────────
app_logger = get_logger("findbug.app")
security_logger = get_logger("findbug.security")
audit_logger = get_logger("findbug.audit")
payment_logger = get_logger("findbug.payment")
task_logger = get_logger("findbug.tasks")
