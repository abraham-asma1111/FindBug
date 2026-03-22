"""
Integration Tests: Authentication Flow
Test complete authentication workflow
"""
import pytest


class TestAuthenticationFlow:
    """Test complete authentication flow"""
    
    def test_researcher_registration_and_login(self, client):
        """Test researcher can register and login"""
        # Register
        register_data = {
            "email": "newresearcher@test.com",
            "password": "SecurePass123!",
            "full_name": "New Researcher",
            "role": "researcher"
        }
        response = client.post("/api/v1/auth/register", json=register_data)
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["email"] == register_data["email"]
        
        # Login
        login_data = {
            "email": "newresearcher@test.com",
            "password": "SecurePass123!"
        }
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
    
    def test_organization_registration_and_login(self, client):
        """Test organization can register and login"""
        # Register
        register_data = {
            "email": "neworg@test.com",
            "password": "SecurePass123!",
            "company_name": "New Organization",
            "role": "organization"
        }
        response = client.post("/api/v1/auth/register", json=register_data)
        assert response.status_code == 201
        
        # Login
        login_data = {
            "email": "neworg@test.com",
            "password": "SecurePass123!"
        }
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
    
    def test_invalid_credentials(self, client):
        """Test login with invalid credentials fails"""
        login_data = {
            "email": "nonexistent@test.com",
            "password": "WrongPassword123!"
        }
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code in [401, 404]
    
    def test_duplicate_email_registration(self, client):
        """Test cannot register with duplicate email"""
        register_data = {
            "email": "duplicate@test.com",
            "password": "SecurePass123!",
            "full_name": "First User",
            "role": "researcher"
        }
        
        # First registration
        response = client.post("/api/v1/auth/register", json=register_data)
        assert response.status_code == 201
        
        # Duplicate registration
        response = client.post("/api/v1/auth/register", json=register_data)
        assert response.status_code in [400, 409]
    
    def test_protected_endpoint_without_token(self, client):
        """Test accessing protected endpoint without token fails"""
        response = client.get("/api/v1/profile/me")
        assert response.status_code == 401
    
    def test_protected_endpoint_with_token(self, client, researcher_token):
        """Test accessing protected endpoint with valid token"""
        headers = {"Authorization": f"Bearer {researcher_token}"}
        response = client.get("/api/v1/profile/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "email" in data
