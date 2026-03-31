"""
Integration Tests: Health Check and Endpoint Registration
Test that all endpoints are properly registered after merge
"""
import pytest


def test_health_check(client):
    """Test health endpoint is accessible"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_root_endpoint(client):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


def test_openapi_docs(client):
    """Test API documentation is accessible"""
    response = client.get("/docs")
    assert response.status_code == 200


def test_all_endpoints_registered(client):
    """Test that all 23 endpoint modules are registered"""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    
    openapi_spec = response.json()
    paths = openapi_spec.get("paths", {})
    
    # Check critical endpoint groups exist
    endpoint_groups = [
        "/api/v1/auth",
        "/api/v1/programs",
        "/api/v1/reports",
        "/api/v1/triage",
        "/api/v1/bounty",
        "/api/v1/leaderboard",
        "/api/v1/notifications",
        "/api/v1/dashboard",
        "/api/v1/analytics",
        "/api/v1/admin",
        "/api/v1/matching",
        "/api/v1/ptaas",
        "/api/v1/code-review",
        "/api/v1/integration",
        "/api/v1/live-events",
        "/api/v1/ai-red-teaming",
        "/api/v1/messages",
        "/api/v1/subscription",
        "/api/v1/financial",
        "/api/v1/simulation",
    ]
    
    # Verify at least one endpoint from each group exists
    for group in endpoint_groups:
        matching_paths = [path for path in paths.keys() if path.startswith(group)]
        assert len(matching_paths) > 0, f"No endpoints found for {group}"


def test_cors_headers(client):
    """Test CORS is properly configured"""
    response = client.options("/health", headers={
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "GET"
    })
    # CORS should allow the request
    assert response.status_code in [200, 204]
