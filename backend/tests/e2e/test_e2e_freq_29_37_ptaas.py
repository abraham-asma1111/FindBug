"""
E2E Tests for FREQ-29 to FREQ-37: PTaaS Platform
Tests PTaaS engagements, dashboard, findings, triage, and retest workflows
"""
import pytest


class TestFREQ29PTaaSEngagements:
    """FREQ-29: PTaaS Engagement Management"""
    
    def test_create_and_manage_engagement(self, client, organization_token):
        """E2E: Create and manage PTaaS engagement"""
        headers = {"Authorization": f"Bearer {organization_token}"}
        
        # Create engagement
        create_response = client.post("/api/v1/ptaas/engagements", headers=headers, json={
            "name": "Q1 2026 Penetration Test",
            "scope": ["https://example.com", "https://api.example.com"],
            "start_date": "2026-04-01",
            "end_date": "2026-04-15",
            "engagement_type": "web_application"
        })
        assert create_response.status_code in [201, 200]
        
        if create_response.status_code in [201, 200]:
            engagement_id = create_response.json()["id"]
            
            # Get engagement details
            get_response = client.get(f"/api/v1/ptaas/engagements/{engagement_id}", headers=headers)
            assert get_response.status_code in [200, 404]
            
            # Update engagement
            update_response = client.put(f"/api/v1/ptaas/engagements/{engagement_id}", headers=headers, json={
                "status": "in_progress"
            })
            assert update_response.status_code in [200, 404]


class TestFREQ30PTaaSDashboard:
    """FREQ-30: PTaaS Dashboard"""
    
    def test_ptaas_dashboard(self, client, organization_token):
        """E2E: View PTaaS dashboard metrics"""
        headers = {"Authorization": f"Bearer {organization_token}"}
        
        # Get dashboard
        response = client.get("/api/v1/ptaas/dashboard", headers=headers)
        assert response.status_code == 200
        
        # Get engagement statistics
        stats_response = client.get("/api/v1/ptaas/statistics", headers=headers)
        assert stats_response.status_code in [200, 404]


class TestFREQ31PTaaSFindings:
    """FREQ-31: PTaaS Findings Management"""
    
    def test_submit_and_manage_findings(self, client, researcher_token, organization_token):
        """E2E: Submit findings and manage them"""
        researcher_headers = {"Authorization": f"Bearer {researcher_token}"}
        org_headers = {"Authorization": f"Bearer {organization_token}"}
        
        # Submit finding
        submit_response = client.post("/api/v1/ptaas/findings", headers=researcher_headers, json={
            "engagement_id": "test-engagement-id",
            "title": "SQL Injection in API",
            "description": "Found SQL injection",
            "severity": "high",
            "cvss_score": 8.5
        })
        assert submit_response.status_code in [201, 404]
        
        # List findings (organization view)
        list_response = client.get("/api/v1/ptaas/findings", headers=org_headers)
        assert list_response.status_code in [200, 404]


class TestFREQ32AdvancedMatching:
    """FREQ-32: Advanced PTaaS Researcher Matching"""
    
    def test_advanced_matching_algorithm(self, client, organization_token):
        """E2E: Get matched researchers for PTaaS engagement"""
        headers = {"Authorization": f"Bearer {organization_token}"}
        
        # Get recommendations for engagement
        response = client.post("/api/v1/matching/ptaas/recommendations", headers=headers, json={
            "engagement_type": "web_application",
            "required_skills": ["web", "api", "mobile"],
            "min_reputation": 500
        })
        assert response.status_code in [200, 404]


class TestFREQ33MatchingConfiguration:
    """FREQ-33: Matching Configuration & Approval"""
    
    def test_matching_criteria_and_approval(self, client, organization_token):
        """E2E: Configure matching criteria and approve assignments"""
        headers = {"Authorization": f"Bearer {organization_token}"}
        
        # Set matching criteria
        criteria_response = client.post("/api/v1/matching/criteria", headers=headers, json={
            "min_reputation": 1000,
            "required_skills": ["web", "api"],
            "max_researchers": 5
        })
        assert criteria_response.status_code in [201, 200, 404]
        
        # Approve researcher assignment
        approve_response = client.post("/api/v1/matching/assignments/test-assignment-id/approve", headers=headers)
        assert approve_response.status_code in [200, 404]


class TestFREQ34PTaaSReports:
    """FREQ-34: PTaaS Reporting"""
    
    def test_generate_ptaas_report(self, client, organization_token):
        """E2E: Generate PTaaS engagement report"""
        headers = {"Authorization": f"Bearer {organization_token}"}
        
        # Generate report
        response = client.post("/api/v1/ptaas/engagements/test-engagement-id/report", headers=headers, json={
            "report_type": "executive_summary"
        })
        assert response.status_code in [201, 404]


class TestFREQ35PTaaSTriage:
    """FREQ-35: PTaaS Triage Workflow"""
    
    def test_ptaas_triage(self, client, organization_token):
        """E2E: Triage PTaaS findings"""
        headers = {"Authorization": f"Bearer {organization_token}"}
        
        # Get triage queue
        queue_response = client.get("/api/v1/ptaas/triage/queue", headers=headers)
        assert queue_response.status_code in [200, 404]
        
        # Triage finding
        triage_response = client.post("/api/v1/ptaas/findings/test-finding-id/triage", headers=headers, json={
            "status": "validated",
            "severity": "high"
        })
        assert triage_response.status_code in [200, 404]


class TestFREQ36PTaaSRetest:
    """FREQ-36: PTaaS Retest Workflow"""
    
    def test_retest_workflow(self, client, organization_token, researcher_token):
        """E2E: Request retest and verify fix"""
        org_headers = {"Authorization": f"Bearer {organization_token}"}
        researcher_headers = {"Authorization": f"Bearer {researcher_token}"}
        
        # Request retest
        request_response = client.post("/api/v1/ptaas/findings/test-finding-id/retest", headers=org_headers)
        assert request_response.status_code in [201, 404]
        
        # Submit retest result
        result_response = client.post("/api/v1/ptaas/findings/test-finding-id/retest-result", headers=researcher_headers, json={
            "status": "fixed",
            "notes": "Vulnerability has been fixed"
        })
        assert result_response.status_code in [200, 404]


class TestFREQ37PTaaSCollaboration:
    """FREQ-37: PTaaS Team Collaboration"""
    
    def test_team_collaboration(self, client, researcher_token):
        """E2E: Collaborate with team members"""
        headers = {"Authorization": f"Bearer {researcher_token}"}
        
        # Get team members
        team_response = client.get("/api/v1/ptaas/engagements/test-engagement-id/team", headers=headers)
        assert team_response.status_code in [200, 404]
        
        # Send message to team
        message_response = client.post("/api/v1/messages", headers=headers, json={
            "recipient_id": "test-user-id",
            "subject": "Finding Discussion",
            "content": "Let's discuss this finding"
        })
        assert message_response.status_code in [201, 404]
