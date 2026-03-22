"""
Pytest Configuration and Fixtures
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from src.main import app
from src.core.database import Base, get_db
from src.core.config import settings


# Test Database URL
TEST_DATABASE_URL = "postgresql://test_user:test_pass@localhost:5432/test_bugbounty"


@pytest.fixture(scope="session")
def test_engine():
    """Create test database engine"""
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def test_db(test_engine):
    """Create test database session"""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()


@pytest.fixture(scope="function")
def client(test_db):
    """Create test client with database override"""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def researcher_token(client):
    """Create researcher and return auth token"""
    # Register researcher
    response = client.post("/api/v1/auth/register", json={
        "email": "researcher@test.com",
        "password": "Test123!@#",
        "full_name": "Test Researcher",
        "role": "researcher"
    })
    assert response.status_code == 201
    
    # Login
    response = client.post("/api/v1/auth/login", json={
        "email": "researcher@test.com",
        "password": "Test123!@#"
    })
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def organization_token(client):
    """Create organization and return auth token"""
    # Register organization
    response = client.post("/api/v1/auth/register", json={
        "email": "org@test.com",
        "password": "Test123!@#",
        "company_name": "Test Organization",
        "role": "organization"
    })
    assert response.status_code == 201
    
    # Login
    response = client.post("/api/v1/auth/login", json={
        "email": "org@test.com",
        "password": "Test123!@#"
    })
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def staff_token(client):
    """Create staff and return auth token"""
    # Register staff
    response = client.post("/api/v1/auth/register", json={
        "email": "staff@test.com",
        "password": "Test123!@#",
        "full_name": "Test Staff",
        "role": "staff"
    })
    assert response.status_code == 201
    
    # Login
    response = client.post("/api/v1/auth/login", json={
        "email": "staff@test.com",
        "password": "Test123!@#"
    })
    assert response.status_code == 200
    return response.json()["access_token"]
