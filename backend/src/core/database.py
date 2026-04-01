"""
Database configuration and session management.
"""
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

# Database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is required.")

DISCONNECT_ERROR_MARKERS = (
    "server closed the connection unexpectedly",
    "connection not open",
    "could not connect to server",
    "connection refused",
    "connection reset by peer",
    "terminating connection",
    "closed the connection",
    "ssl connection has been closed unexpectedly",
)


def is_database_disconnect_error(exc: BaseException) -> bool:
    """Return True when SQLAlchemy reports a lost or unavailable DB connection."""
    if isinstance(exc, DBAPIError) and exc.connection_invalidated:
        return True

    message = str(exc).lower()
    return any(marker in message for marker in DISCONNECT_ERROR_MARKERS)


def _engine_kwargs(database_url: str) -> dict:
    """Build engine kwargs with conservative pooling for long-lived API processes."""
    kwargs = {
        "pool_pre_ping": True,
        "pool_recycle": int(os.getenv("DB_POOL_RECYCLE", "300")),
        "pool_size": int(os.getenv("DB_POOL_SIZE", "10")),
        "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", "20")),
        "pool_timeout": int(os.getenv("DB_POOL_TIMEOUT", "30")),
        "pool_use_lifo": True,
    }

    if database_url.startswith("postgresql"):
        kwargs["connect_args"] = {
            "connect_timeout": int(os.getenv("DB_CONNECT_TIMEOUT", "5"))
        }

    return kwargs

# Create engine
engine = create_engine(
    DATABASE_URL,
    **_engine_kwargs(DATABASE_URL),
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Base class for models
Base = declarative_base()


def get_database_status() -> str:
    """Probe the database using the same resilient session factory as the API."""
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        return "healthy"
    except Exception as exc:
        return "unavailable" if is_database_disconnect_error(exc) else "error"
    finally:
        db.close()


# Dependency for FastAPI
def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
