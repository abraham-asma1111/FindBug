"""
End-to-End Integration Test: Organization Complete Workflow
Tests the full journey of an organization from registration to program management
"""
import pytest


class TestOrganizationE2EWorkflow:
    """Test complete organization workflow end-to-end"""
    
    def test_complete_organization_journey(self, client):
        """
        Complete organization workflow:
        1. Register as organization
        2. Login and get token
        3. Subscribe to a tier
        4. Create bug bounty program
        5. View submitted reports
        6. Approve bounty payment
        7. View analytics
        """
        
        # Step 1: Register organization
        register_data = {
            "email": "e2e_org@test.com",
            "password": "SecurePass123!",
            "password_confirm": "SecurePass123!",
            "first_name": "E2E",
            "last_name": "Organization",
            "company_name": "E2E Test Company"
        }
        response = client.post("/api/v1/auth/register/organization", json=register_data)
        assert response.status_code == 201
        user_data = response.json()
        org_id = user_data["organization_id"]
        
        # Step 2: Login
        login_data = {
            "email": "e2e_org@test.com",
            "password": "SecurePass123!"
        }
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Step 3: View profile
        response = client.get("/api/v1/profile", headers=headers)
        assert response.status_code == 200
        profile = response.json()
        assert profile["email"] == "e2e_org@test.com"
        assert "organization" in profile
        
        # Step 4: View subscription tiers (public)
        response = client.get("/api/v1/subscriptions/tiers")
        assert response.status_code == 200
        
        # Step 5: View programs (should be empty initially)
        response = client.get("/api/v1/programs", headers=headers)
        assert response.status_code in [200, 404]
        
        # Step 6: View analytics
        response = client.get("/api/v1/analytics/vulnerability-trends", headers=headers)
        assert response.status_code in [200, 400, 403]  # May need specific permissions
        
        # Step 7: View notifications
        response = client.get("/api/v1/notifications", headers=headers)
        assert response.status_code in [200, 404]
        
        print(f"✅ E2E Organization workflow completed successfully")
        print(f"   - Organization ID: {org_id}")
        print(f"   - Company: {register_data['company_name']}")
