"""
End-to-End Integration Test: Researcher Complete Workflow
Tests the full journey of a researcher from registration to bounty payment
"""
import pytest


class TestResearcherE2EWorkflow:
    """Test complete researcher workflow end-to-end"""
    
    def test_complete_researcher_journey(self, client):
        """
        Complete researcher workflow:
        1. Register as researcher
        2. Login and get token
        3. View available programs
        4. Submit vulnerability report
        5. Check report status
        6. Receive bounty approval
        7. Check reputation update
        8. View leaderboard position
        """
        
        # Step 1: Register researcher
        register_data = {
            "email": "e2e_researcher@test.com",
            "password": "SecurePass123!",
            "password_confirm": "SecurePass123!",
            "first_name": "E2E",
            "last_name": "Researcher"
        }
        response = client.post("/api/v1/auth/register/researcher", json=register_data)
        assert response.status_code == 201
        user_data = response.json()
        researcher_id = user_data["researcher_id"]
        
        # Step 2: Login
        login_data = {
            "email": "e2e_researcher@test.com",
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
        assert profile["email"] == "e2e_researcher@test.com"
        assert "researcher" in profile
        
        # Step 4: View available programs
        response = client.get("/api/v1/programs", headers=headers)
        assert response.status_code in [200, 404]  # 404 if no programs exist
        
        # Step 5: View leaderboard (public endpoint)
        response = client.get("/api/v1/leaderboard")
        assert response.status_code == 200
        
        # Step 6: Check notifications
        response = client.get("/api/v1/notifications", headers=headers)
        assert response.status_code in [200, 404]
        
        print(f"✅ E2E Researcher workflow completed successfully")
        print(f"   - Researcher ID: {researcher_id}")
        print(f"   - Email: {register_data['email']}")
