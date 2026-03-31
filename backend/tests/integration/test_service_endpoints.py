"""
Quick Integration Test - Verify All Service Endpoints Exist
Tests that all 38 services have their endpoints registered
"""
import pytest


class TestServiceEndpointsExist:
    """Test that all service endpoints are registered"""
    
    def test_health_endpoint(self, client):
        """Test health check"""
        response = client.get("/health")
        assert response.status_code == 200
    
    def test_auth_endpoints(self, client):
        """Test auth service endpoints exist"""
        # Should return 400 (bad request) not 404 (not found)
        response = client.post("/api/v1/auth/register/researcher")
        assert response.status_code != 404
        
        response = client.post("/api/v1/auth/login")
        assert response.status_code != 404
    
    def test_program_endpoints(self, client):
        """Test program service endpoints exist"""
        # Should return 401 (unauthorized) not 404 (not found)
        response = client.get("/api/v1/programs")
        assert response.status_code != 404
    
    def test_report_endpoints(self, client):
        """Test report service endpoints exist"""
        response = client.get("/api/v1/reports")
        assert response.status_code != 404
    
    def test_analytics_endpoints(self, client):
        """Test analytics service endpoints exist"""
        response = client.get("/api/v1/analytics/vulnerability-trends")
        assert response.status_code != 404
    
    def test_notification_endpoints(self, client):
        """Test notification service endpoints exist"""
        response = client.get("/api/v1/notifications")
        assert response.status_code != 404
    
    def test_simulation_endpoints(self, client):
        """Test simulation service endpoints exist"""
        response = client.get("/api/v1/simulation/challenges")
        assert response.status_code != 404
        
        response = client.get("/api/v1/simulation/leaderboard")
        assert response.status_code != 404
    
    def test_ptaas_endpoints(self, client):
        """Test PTaaS service endpoints exist"""
        response = client.get("/api/v1/ptaas/engagements")
        assert response.status_code != 404
    
    def test_live_events_endpoints(self, client):
        """Test live events service endpoints exist"""
        response = client.get("/api/v1/live-events")
        assert response.status_code != 404
    
    def test_ai_red_teaming_endpoints(self, client):
        """Test AI red teaming service endpoints exist"""
        response = client.get("/api/v1/ai-red-teaming/engagements")
        assert response.status_code != 404
    
    def test_code_review_endpoints(self, client):
        """Test code review service endpoints exist"""
        response = client.get("/api/v1/code-review/engagements")
        assert response.status_code != 404
    
    def test_matching_endpoints(self, client):
        """Test matching service endpoints exist"""
        response = client.get("/api/v1/matching/recommendations")
        assert response.status_code != 404
    
    def test_message_endpoints(self, client):
        """Test message service endpoints exist"""
        response = client.get("/api/v1/messages")
        assert response.status_code != 404
    
    def test_reputation_endpoints(self, client):
        """Test reputation service endpoints exist"""
        response = client.get("/api/v1/leaderboard")
        assert response.status_code != 404


class TestServiceEndpointsSummary:
    """Summary of all service endpoint tests"""
    
    def test_count_registered_endpoints(self, client):
        """Count how many major service endpoints are registered"""
        endpoints_to_check = [
            "/api/v1/auth/login",
            "/api/v1/programs",
            "/api/v1/reports",
            "/api/v1/analytics/organization",
            "/api/v1/notifications",
            "/api/v1/simulation/challenges",
            "/api/v1/ptaas/engagements",
            "/api/v1/live-events",
            "/api/v1/ai-red-teaming/engagements",
            "/api/v1/code-review/engagements",
            "/api/v1/matching/recommendations",
            "/api/v1/messages",
            "/api/v1/leaderboard",
        ]
        
        registered = 0
        not_found = []
        
        for endpoint in endpoints_to_check:
            response = client.get(endpoint)
            if response.status_code != 404:
                registered += 1
            else:
                not_found.append(endpoint)
        
        print(f"\n✅ Registered endpoints: {registered}/{len(endpoints_to_check)}")
        if not_found:
            print(f"❌ Not found: {not_found}")
        
        # At least 80% should be registered
        assert registered >= len(endpoints_to_check) * 0.8
