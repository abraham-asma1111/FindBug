"""
API Endpoint Integration Tests - Complete Coverage
Tests all API endpoints with comprehensive validation
"""

import pytest
import json
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

class TestAPIEndpoints:
    """Complete API endpoint test suite"""
    
    # FREQ-01: Authentication Tests
    def test_auth_registration(self):
        """Test user registration endpoint"""
        response = client.post("/api/v1/auth/register", json={
            "email": "test@example.com",
            "password": "TestPass123!",
            "full_name": "Test User",
            "role": "researcher"
        })
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "user_id" in data

    def test_auth_login(self):
        """Test user login endpoint"""
        response = client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "TestPass123!"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "access_token" in data

    # FREQ-02: Report Submission Tests
    def test_report_submission(self):
        """Test report submission endpoint"""
        # First login to get token
        login_response = client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "TestPass123!"
        })
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.post("/api/v1/reports", json={
            "title": "Test Vulnerability",
            "description": "Test description",
            "severity": "high",
            "steps_to_reproduce": ["1. Test step"],
            "impact": "Test impact",
            "program_id": "test-program-id"
        }, headers=headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True

    # FREQ-03-08: Program Management Tests
    def test_program_creation(self):
        """Test program creation endpoint"""
        login_response = client.post("/api/v1/auth/login", json={
            "email": "org@example.com",
            "password": "OrgPass123!"
        })
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.post("/api/v1/programs", json={
            "name": "Test Program",
            "description": "Test program description",
            "program_type": "public",
            "scope": {"in_scope": ["test.com"], "out_of_scope": ["admin.test.com"]},
            "reward_tiers": {"critical": 5000, "high": 1000, "medium": 500, "low": 100},
            "rules": "Test rules"
        }, headers=headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Program"

    # FREQ-10: Payment Tests
    def test_bounty_approval(self):
        """Test bounty approval endpoint"""
        login_response = client.post("/api/v1/auth/login", json={
            "email": "admin@example.com",
            "password": "AdminPass123!"
        })
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.post("/api/v1/bounty/approve", json={
            "report_id": "test-report-id",
            "amount": 1000,
            "approved_by": "admin-user-id"
        }, headers=headers)
        
        assert response.status_code == 200

    # FREQ-11: Reputation Tests
    def test_reputation_system(self):
        """Test reputation system endpoint"""
        response = client.get("/api/v1/reputation/test-user-id")
        assert response.status_code == 200
        data = response.json()
        assert "total_score" in data
        assert "rank" in data

    # FREQ-12: Analytics Tests
    def test_analytics_endpoint(self):
        """Test analytics endpoint"""
        login_response = client.post("/api/v1/auth/login", json={
            "email": "org@example.com",
            "password": "OrgPass123!"
        })
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/api/v1/analytics/organization/test-org-id", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "vulnerability_trends" in data

    # FREQ-13: Notification Tests
    def test_notifications_endpoint(self):
        """Test notifications endpoint"""
        login_response = client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "TestPass123!"
        })
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/api/v1/notifications/user/test-user-id", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    # FREQ-16: Triage Tests
    def test_triage_endpoint(self):
        """Test triage endpoint"""
        login_response = client.post("/api/v1/auth/login", json={
            "email": "triage@example.com",
            "password": "TriagePass123!"
        })
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.post("/api/v1/triage/validate", json={
            "report_id": "test-report-id",
            "severity": "high",
            "status": "valid",
            "comments": "Validated by triage"
        }, headers=headers)
        
        assert response.status_code == 200

    # FREQ-22: KYC Tests
    def test_kyc_submission(self):
        """Test KYC submission endpoint"""
        login_response = client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "TestPass123!"
        })
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.post("/api/v1/kyc/submit", json={
            "document_type": "passport",
            "document_number": "P123456789"
        }, headers=headers)
        
        assert response.status_code == 201

    # FREQ-29-31: PTaaS Tests
    def test_ptaas_creation(self):
        """Test PTaaS creation endpoint"""
        login_response = client.post("/api/v1/auth/login", json={
            "email": "org@example.com",
            "password": "OrgPass123!"
        })
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.post("/api/v1/ptaas/engagement", json={
            "scope": "test.com",
            "methodology": "OWASP",
            "start_date": "2026-03-29T00:00:00Z",
            "end_date": "2026-04-28T00:00:00Z",
            "pricing_model": "fixed"
        }, headers=headers)
        
        assert response.status_code == 201

    # FREQ-32-33: Matching Tests
    def test_matching_recommendations(self):
        """Test matching recommendations endpoint"""
        login_response = client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "TestPass123!"
        })
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/api/v1/matching/recommendations/test-user-id", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "programs" in data

    # FREQ-41: Code Review Tests
    def test_code_review_creation(self):
        """Test code review creation endpoint"""
        login_response = client.post("/api/v1/auth/login", json={
            "email": "org@example.com",
            "password": "OrgPass123!"
        })
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.post("/api/v1/code_review/create", json={
            "repository_url": "https://github.com/test/repo",
            "branch": "main",
            "review_type": "security",
            "scope": "full_scan"
        }, headers=headers)
        
        assert response.status_code == 201

    # FREQ-42: SSDLC Integration Tests
    def test_ssdcl_github_integration(self):
        """Test SSDLC GitHub integration endpoint"""
        login_response = client.post("/api/v1/auth/login", json={
            "email": "org@example.com",
            "password": "OrgPass123!"
        })
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.post("/api/v1/ssdlc/github", json={
            "repository_url": "https://github.com/test/repo",
            "api_key": "test_key",
            "webhook_secret": "test_secret"
        }, headers=headers)
        
        assert response.status_code == 201

    # FREQ-43-44: Live Event Tests
    def test_live_event_creation(self):
        """Test live event creation endpoint"""
        login_response = client.post("/api/v1/auth/login", json={
            "email": "org@example.com",
            "password": "OrgPass123!"
        })
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.post("/api/v1/live_events/create", json={
            "name": "Test Live Event",
            "description": "Test event description",
            "start_time": "2026-03-29T00:00:00Z",
            "end_time": "2026-03-30T00:00:00Z",
            "scope": "*.test.com",
            "reward_structure": {"high": 2000, "medium": 1000}
        }, headers=headers)
        
        assert response.status_code == 201

    # FREQ-45-48: AI Red Teaming Tests
    def test_ai_red_teaming_creation(self):
        """Test AI Red Teaming creation endpoint"""
        login_response = client.post("/api/v1/auth/login", json={
            "email": "org@example.com",
            "password": "OrgPass123!"
        })
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.post("/api/v1/ai_red_teaming/engagement", json={
            "ai_targets": ["test_ai_system"],
            "methodology": "ai_red_teaming_v1",
            "ethical_guidelines": "Responsible AI testing",
            "scope": "authorized_ai_environment_only"
        }, headers=headers)
        
        assert response.status_code == 201

    # File Upload Tests
    def test_file_upload(self):
        """Test file upload endpoint"""
        login_response = client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "TestPass123!"
        })
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test file upload
        with open("test_file.txt", "w") as f:
            f.write("Test file content")
        
        with open("test_file.txt", "rb") as f:
            response = client.post(
                "/api/v1/files/upload",
                files={"file": ("test_file.txt", f, "text/plain")},
                data={"user_id": "test-user-id"},
                headers=headers
            )
        
        assert response.status_code == 201

    # Email Preferences Tests
    def test_email_preferences(self):
        """Test email preferences endpoint"""
        response = client.get("/api/v1/email-preferences/test-user-id")
        assert response.status_code == 200
        data = response.json()
        assert "report_updates" in data

    # Payment Methods Tests
    def test_payment_methods(self):
        """Test payment methods endpoint"""
        response = client.get("/api/v1/payment-methods/test-user-id")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    # Duplicate Detection Tests
    def test_duplicate_detection(self):
        """Test duplicate detection endpoint"""
        response = client.post("/api/v1/duplicate-detection/check", json={
            "title": "Test Vulnerability",
            "description": "Test description",
            "program_id": "test-program-id",
            "user_id": "test-user-id"
        })
        assert response.status_code == 200
        data = response.json()
        assert "is_duplicate" in data

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
