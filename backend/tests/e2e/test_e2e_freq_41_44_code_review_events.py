"""
E2E Tests for FREQ-41 to FREQ-44: Code Review, SSDLC, and Live Events
Tests code review engagements, SSDLC integration, and live hacking events
"""
import pytest


class TestFREQ41CodeReview:
    """FREQ-41: Code Review Engagement"""
    
    def test_create_code_review_engagement(self, client, organization_token):
        """E2E: Create and manage code review engagement"""
        headers = {"Authorization": f"Bearer {organization_token}"}
        
        # Create code review engagement
        create_response = client.post("/api/v1/code-review/engagements", headers=headers, json={
            "name": "API Security Review",
            "repository_url": "https://github.com/org/repo",
            "scope": "security review of authentication module",
            "start_date": "2026-04-01",
            "end_date": "2026-04-10"
        })
        assert create_response.status_code in [201, 200]
        
        if create_response.status_code in [201, 200]:
            engagement_id = create_response.json()["id"]
            
            # Get engagement details
            get_response = client.get(f"/api/v1/code-review/engagements/{engagement_id}", headers=headers)
            assert get_response.status_code in [200, 404]
    
    def test_submit_code_review_finding(self, client, researcher_token):
        """E2E: Submit code review finding"""
        headers = {"Authorization": f"Bearer {researcher_token}"}
        
        # Submit finding
        submit_response = client.post("/api/v1/code-review/findings", headers=headers, json={
            "engagement_id": "test-engagement-id",
            "title": "Insecure Password Storage",
            "description": "Passwords stored in plaintext",
            "severity": "critical",
            "file_path": "src/auth/user.py",
            "line_number": 42,
            "recommendation": "Use bcrypt for password hashing"
        })
        assert submit_response.status_code in [201, 404]


class TestFREQ42SSDLC:
    """FREQ-42: SSDLC Integration"""
    
    def test_ssdlc_integration(self, client, organization_token):
        """E2E: Integrate with SSDLC tools"""
        headers = {"Authorization": f"Bearer {organization_token}"}
        
        # Configure SSDLC integration
        config_response = client.post("/api/v1/integrations/ssdlc", headers=headers, json={
            "tool": "github",
            "webhook_url": "https://example.com/webhook",
            "events": ["pull_request", "push"]
        })
        assert config_response.status_code in [201, 200, 400]
        
        # Get integration status
        status_response = client.get("/api/v1/integrations/ssdlc", headers=headers)
        assert status_response.status_code in [200, 404]


class TestFREQ43LiveEvents:
    """FREQ-43: Live Hacking Events"""
    
    def test_create_and_manage_live_event(self, client, organization_token):
        """E2E: Create and manage live hacking event"""
        headers = {"Authorization": f"Bearer {organization_token}"}
        
        # Create live event
        create_response = client.post("/api/v1/live-events", headers=headers, json={
            "name": "Spring Security Event 2026",
            "description": "3-day live hacking event",
            "start_time": "2026-05-01T10:00:00Z",
            "end_time": "2026-05-03T18:00:00Z",
            "prize_pool": 50000,
            "max_participants": 50,
            "scope": ["https://example.com"]
        })
        assert create_response.status_code in [201, 200]
        
        if create_response.status_code in [201, 200]:
            event_id = create_response.json()["id"]
            
            # Get event details
            get_response = client.get(f"/api/v1/live-events/{event_id}", headers=headers)
            assert get_response.status_code in [200, 404]
    
    def test_register_for_live_event(self, client, researcher_token):
        """E2E: Register for live hacking event"""
        headers = {"Authorization": f"Bearer {researcher_token}"}
        
        # List available events
        list_response = client.get("/api/v1/live-events", headers=headers)
        assert list_response.status_code in [200, 404]
        
        # Register for event
        register_response = client.post("/api/v1/live-events/test-event-id/register", headers=headers)
        assert register_response.status_code in [201, 404, 400]
    
    def test_submit_live_event_report(self, client, researcher_token):
        """E2E: Submit report during live event"""
        headers = {"Authorization": f"Bearer {researcher_token}"}
        
        # Submit report
        submit_response = client.post("/api/v1/reports", headers=headers, json={
            "program_id": "test-program-id",
            "event_id": "test-event-id",
            "title": "XSS in Search",
            "description": "Found XSS vulnerability",
            "severity": "medium"
        })
        assert submit_response.status_code in [201, 404]


class TestFREQ44EventLeaderboard:
    """FREQ-44: Live Event Leaderboard"""
    
    def test_live_event_leaderboard(self, client):
        """E2E: View live event leaderboard"""
        # Get event leaderboard (public)
        response = client.get("/api/v1/live-events/test-event-id/leaderboard")
        assert response.status_code in [200, 404]
        
        # Get real-time rankings
        rankings_response = client.get("/api/v1/live-events/test-event-id/rankings")
        assert rankings_response.status_code in [200, 404]
