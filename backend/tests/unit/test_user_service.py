import pytest
from unittest.mock import MagicMock
from src.services.user_service import UserService
from src.core.exceptions import NotFoundException, ForbiddenException
from src.domain.models.user import User
from src.domain.models.researcher import Researcher
from src.domain.models.organization import Organization


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def user_service(mock_db):
    service = UserService(mock_db)
    service.user_repo = MagicMock()
    service.researcher_repo = MagicMock()
    service.org_repo = MagicMock()
    return service


def test_get_profile_not_found(user_service):
    user_service.user_repo.get_by_id.return_value = None

    with pytest.raises(NotFoundException):
        user_service.get_profile("missing_id")


def test_get_researcher_profile(user_service):
    mock_user = User(
        id="u1", email="test@ninja.com", role="researcher"
    )
    mock_researcher = Researcher(
        user_id="u1", reputation_score=150, rank=1, total_earnings=250.0
    )

    user_service.user_repo.get_by_id.return_value = mock_user
    user_service.researcher_repo.get_by_user_id.return_value = mock_researcher

    profile = user_service.get_profile("u1")

    assert profile["id"] == "u1"
    assert profile["email"] == "test@ninja.com"
    assert profile["role"] == "researcher"
    assert "researcher" in profile
    assert profile["researcher"]["reputation_score"] == 150
    assert profile["researcher"]["total_earnings"] == 250.0


def test_get_organization_profile(user_service):
    mock_user = User(
        id="u2", email="admin@corp.com", role="organization"
    )
    mock_org = Organization(
        user_id="u2", company_name="Corp Inc", industry="Tech"
    )

    user_service.user_repo.get_by_id.return_value = mock_user
    user_service.org_repo.get_by_user_id.return_value = mock_org

    profile = user_service.get_profile("u2")

    assert profile["role"] == "organization"
    assert "organization" in profile
    assert profile["organization"]["company_name"] == "Corp Inc"


def test_update_profile_forbidden(user_service):
    # User tries to update someone else's profile
    with pytest.raises(ForbiddenException):
        user_service.update_profile("u1", {"bio": "Hack"}, "u2")


def test_update_profile_success(user_service):
    mock_user = User(id="u1", email="test@example.com", role="researcher")
    mock_researcher = Researcher(user_id="u1")

    user_service.user_repo.get_by_id.return_value = mock_user
    user_service.researcher_repo.get_by_user_id.return_value = mock_researcher

    # Mock the internal call to get_profile to return the updated payload
    user_service.get_profile = MagicMock(return_value={"id": "u1", "email": "test@example.com"})

    data = {
        "profile": {
            "bio": "I find bugs."
        }
    }

    result = user_service.update_profile("u1", data, "u1")

    # Assert model attributes were updated
    assert mock_researcher.bio == "I find bugs."
    user_service.db.commit.assert_called()
    assert result["id"] == "u1"


def test_deactivate_user(user_service):
    mock_user = User(id="u1", is_active=True)
    user_service.user_repo.get_by_id.return_value = mock_user

    result = user_service.deactivate_user("u1")

    assert mock_user.is_active is False
    user_service.db.commit.assert_called_once()
    assert result["user_id"] == "u1"
