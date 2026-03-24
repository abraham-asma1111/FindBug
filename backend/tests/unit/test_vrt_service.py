import pytest
from unittest.mock import MagicMock
from src.services.vrt_service import VRTService
from src.domain.models.vrt import VRTCategory, VRTEntry
from src.core.exceptions import NotFoundException


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def vrt_service(mock_db):
    service = VRTService(mock_db)
    service.repo = MagicMock()
    return service


def test_get_all_categories(vrt_service):
    # Setup mock
    mock_cat = VRTCategory(
        id="c1", name="Injection", slug="injection", is_active=True
    )
    vrt_service.repo.get_all_categories.return_value = [mock_cat]

    # Execute
    result = vrt_service.get_all_categories()

    # Assert
    assert len(result) == 1
    assert result[0]["name"] == "Injection"
    assert result[0]["slug"] == "injection"
    vrt_service.repo.get_all_categories.assert_called_once_with(active_only=True)


def test_get_category_not_found(vrt_service):
    vrt_service.repo.get_by_id.return_value = None

    with pytest.raises(NotFoundException) as exc:
        vrt_service.get_category("missing_id")
    
    assert "not found" in str(exc.value).lower()


def test_get_category_success(vrt_service):
    mock_cat = VRTCategory(id="c1", name="Stored XSS", slug="stored-xss")
    mock_entry = VRTEntry(id="e1", category_id="c1", name="Blind XSS", cvss_min=7.0)
    
    vrt_service.repo.get_by_id.return_value = mock_cat
    vrt_service.repo.get_entries_by_category.return_value = [mock_entry]

    result = vrt_service.get_category("c1")

    assert result["id"] == "c1"
    assert result["name"] == "Stored XSS"
    assert len(result["entries"]) == 1
    assert result["entries"][0]["id"] == "e1"


def test_search_vrt_empty_query(vrt_service):
    # If query is too short, should return empty list without hitting DB
    result = vrt_service.search_vrt("a")
    assert result == []
    vrt_service.repo.search_entries.assert_not_called()


def test_search_vrt_success(vrt_service):
    mock_entry = VRTEntry(id="e1", name="SQL Injection")
    vrt_service.repo.search_entries.return_value = [mock_entry]

    result = vrt_service.search_vrt("SQL")

    assert len(result) == 1
    assert result[0]["name"] == "SQL Injection"
    vrt_service.repo.search_entries.assert_called_once_with("SQL", limit=20)
