"""
Regression tests for database disconnect handling.
"""
from unittest.mock import Mock

from sqlalchemy.exc import OperationalError

from src.core import database as database_module
from src.domain.repositories.user_repository import UserRepository


def test_is_database_disconnect_error_detects_dropped_connection():
    """Dropped PostgreSQL connections should be identified as transient disconnects."""
    error = OperationalError(
        "SELECT 1",
        {},
        Exception("server closed the connection unexpectedly"),
    )

    assert database_module.is_database_disconnect_error(error) is True


def test_get_database_status_reports_unavailable_for_disconnects(monkeypatch):
    """The database health probe should expose connectivity loss as unavailable."""

    class BrokenSession:
        def execute(self, statement):
            raise OperationalError(
                "SELECT 1",
                {},
                Exception("server closed the connection unexpectedly"),
            )

        def close(self):
            return None

    monkeypatch.setattr(database_module, "SessionLocal", lambda: BrokenSession())

    assert database_module.get_database_status() == "unavailable"


def test_user_repository_get_by_id_casts_string_uuid():
    """Repository lookups should normalize string UUIDs before querying."""
    repo = UserRepository(db=Mock())
    query = repo.db.query.return_value
    filtered = query.filter.return_value
    filtered.first.return_value = "uuid-user"

    user_id = "2f580f30-9c60-47a4-9951-1faaaf9dfc4d"
    resolved_user = repo.get_by_id(user_id)

    assert resolved_user == "uuid-user"
    repo.db.query.assert_called_once()
    query.filter.assert_called_once()
    filtered.first.assert_called_once()
