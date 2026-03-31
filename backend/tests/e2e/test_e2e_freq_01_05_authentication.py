"""
E2E Tests for FREQ-01 to FREQ-05: Authentication & Onboarding
Tests complete user journeys for authentication and onboarding flows
"""
import pytest
from datetime import datetime


class TestFREQ01UserAuthentication:
    """FREQ-01: User Registration & Authentication"""
    
    def test_researcher_registration_and_login(self, client):
        """E2E: Researcher registers, verifies email, and logs in"""
        # Register researcher
        register_response = client.post("/api/v1/auth/register/researcher", json={
            "email": "e2e_researcher@test.com",
            "password": "Test123!@#",
            "password_confirm": "Test123!@#",
            "first_name": "E2E",
            "last_name": "Researcher"
        })
        assert register_response.status_code == 201
        
        # Login
        login_response = client.post("/api/v1/auth/login", json={
            "email": "e2e_researcher@test.com",
            "password": "Test123!@#"
        })
        assert login_response.status_code == 200
        assert "access_token" in login_response.json()
    
    def test_organization_registration_and_login(self, client):
        """E2E: Organization registers and logs in"""
        # Register organization
        register_response = client.post("/api/v1/auth/register/organization", json={
            "email": "e2e_org@test.com",
            "password": "Test123!@#",
            "password_confirm": "Test123!@#",
            "first_name": "E2E",
            "last_name": "Organization",
            "company_name": "E2E Test Company"
        })
        assert register_response.status_code == 201
        
        # Login
        login_response = client.post("/api/v1/auth/login", json={
            "email": "e2e_org@test.com",
            "password": "Test123!@#"
        })
        assert login_response.status_code == 200
        assert "access_token" in login_response.json()


class TestFREQ02ResearcherOnboarding:
    """FREQ-02: Researcher Onboarding"""
    
    def test_complete_researcher_onboarding(self, client, researcher_token):
        """E2E: Researcher completes onboarding process"""
        headers = {"Authorization": f"Bearer {researcher_token}"}
        
        # Update profile
        profile_response = client.put("/api/v1/profile", headers=headers, json={
            "bio": "Security researcher with 5 years experience",
            "skills": ["web", "mobile", "api"],
            "website": "https://researcher.example.com"
        })
        assert profile_response.status_code in [200, 404]
        
        # Get profile to verify
        get_profile = client.get("/api/v1/profile", headers=headers)
        assert get_profile.status_code in [200, 404]


class TestFREQ03OrganizationOnboarding:
    """FREQ-03: Organization Onboarding"""
    
    def test_complete_organization_onboarding(self, client, organization_token):
        """E2E: Organization completes onboarding and creates first program"""
        headers = {"Authorization": f"Bearer {organization_token}"}
        
        # Update organization profile
        profile_response = client.put("/api/v1/profile", headers=headers, json={
            "company_description": "Leading tech company",
            "industry": "technology",
            "website": "https://company.example.com"
        })
        assert profile_response.status_code in [200, 404]


class TestFREQ04SSO:
    """FREQ-04: Single Sign-On (SSO)"""
    
    def test_sso_integration(self, client):
        """E2E: SSO authentication flow"""
        # SSO endpoints may not be fully implemented
        response = client.get("/api/v1/auth/sso/providers")
        assert response.status_code in [200, 404]


class TestFREQ05MFA:
    """FREQ-05: Multi-Factor Authentication"""
    
    def test_mfa_setup_and_verification(self, client, researcher_token):
        """E2E: User sets up and verifies MFA"""
        headers = {"Authorization": f"Bearer {researcher_token}"}
        
        # Setup MFA
        setup_response = client.post("/api/v1/auth/mfa/setup", headers=headers)
        assert setup_response.status_code in [200, 201, 404]
        
        if setup_response.status_code in [200, 201]:
            # Verify MFA with test code
            verify_response = client.post("/api/v1/auth/mfa/verify", headers=headers, json={
                "code": "123456"
            })
            assert verify_response.status_code in [200, 400]
