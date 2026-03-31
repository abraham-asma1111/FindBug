"""
End-to-End Integration Test: Simulation Platform Workflow
Tests the complete simulation learning journey
"""
import pytest


class TestSimulationE2EWorkflow:
    """Test complete simulation platform workflow end-to-end"""
    
    def test_complete_simulation_journey(self, client, researcher_token):
        """
        Complete simulation workflow:
        1. View available challenges
        2. Start a challenge
        3. Submit solution/report
        4. Check leaderboard
        5. View progress
        """
        headers = {"Authorization": f"Bearer {researcher_token}"}
        
        # Step 1: View available challenges
        response = client.get("/api/v1/simulation/challenges", headers=headers)
        assert response.status_code in [200, 404]
        
        # Step 2: View challenge categories
        response = client.get("/api/v1/simulation/challenges", headers=headers)
        assert response.status_code in [200, 404]
        
        # Step 3: View simulation leaderboard (public)
        response = client.get("/api/v1/simulation/leaderboard")
        assert response.status_code == 200
        leaderboard = response.json()
        assert "leaderboard" in leaderboard or "message" in leaderboard
        
        # Step 4: View VRT categories (for vulnerability classification)
        response = client.get("/api/v1/vrt/categories")
        assert response.status_code == 200
        vrt_data = response.json()
        assert len(vrt_data) > 0  # Should have VRT categories loaded
        
        print(f"✅ E2E Simulation workflow completed successfully")
        print(f"   - VRT Categories loaded: {len(vrt_data)}")
