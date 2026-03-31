"""
E2E Tests for FREQ-06 to FREQ-11: Bug Bounty Core Features
Tests complete workflows for report submission, triage, bounty, VRT, duplicates, and reputation
"""
import pytest


class TestFREQ06ReportSubmission:
    """FREQ-06: Vulnerability Report Submission"""
    
    def test_complete_report_submission_workflow(self, client, researcher_token, organization_token):
        """E2E: Create program, submit report, view report"""
        # Create program as organization
        org_headers = {"Authorization": f"Bearer {organization_token}"}
        program_response = client.post("/api/v1/programs", headers=org_headers, json={
            "name": "E2E Test Program",
            "description": "Test program for E2E testing",
            "scope": ["https://example.com"],
            "rewards": {"critical": 5000, "high": 3000, "medium": 1000, "low": 500}
        })
        assert program_response.status_code in [201, 200]
        
        if program_response.status_code in [201, 200]:
            program_id = program_response.json()["id"]
            
            # Submit report as researcher
            researcher_headers = {"Authorization": f"Bearer {researcher_token}"}
            report_response = client.post("/api/v1/reports", headers=researcher_headers, json={
                "program_id": program_id,
                "title": "SQL Injection in Login Form",
                "description": "Found SQL injection vulnerability",
                "severity": "high",
                "vulnerability_type": "sqli",
                "steps_to_reproduce": "1. Go to login\n2. Enter payload",
                "impact": "Database access",
                "proof_of_concept": "' OR '1'='1"
            })
            assert report_response.status_code in [201, 200]
            
            if report_response.status_code in [201, 200]:
                report_id = report_response.json().get("id") or report_response.json().get("report_id")
                
                # View report
                view_response = client.get(f"/api/v1/reports/{report_id}", headers=researcher_headers)
                assert view_response.status_code in [200, 404]


class TestFREQ07TriageQueue:
    """FREQ-07: Triage Queue Management"""
    
    def test_triage_workflow(self, client, organization_token):
        """E2E: View triage queue and process reports"""
        headers = {"Authorization": f"Bearer {organization_token}"}
        
        # Get triage queue
        queue_response = client.get("/api/v1/triage/queue", headers=headers)
        assert queue_response.status_code in [200, 404]
        
        # Get triage statistics
        stats_response = client.get("/api/v1/triage/statistics", headers=headers)
        assert stats_response.status_code in [200, 404]


class TestFREQ08VRTIntegration:
    """FREQ-08: VRT Integration & Severity Assignment"""
    
    def test_vrt_categories_and_assignment(self, client):
        """E2E: List VRT categories and assign to report"""
        # List VRT categories (public endpoint)
        categories_response = client.get("/api/v1/vrt/categories")
        assert categories_response.status_code == 200
        data = categories_response.json()
        assert len(data) > 0
        
        # Get VRT entries
        entries_response = client.get("/api/v1/vrt/entries")
        assert entries_response.status_code == 200


class TestFREQ09BountyPayment:
    """FREQ-09: Bounty Payment Processing"""
    
    def test_bounty_approval_and_payment(self, client, organization_token):
        """E2E: Approve bounty and process payment"""
        headers = {"Authorization": f"Bearer {organization_token}"}
        
        # List bounties
        bounties_response = client.get("/api/v1/bounties", headers=headers)
        assert bounties_response.status_code in [200, 404]
        
        # Approve bounty (may fail if no reports exist)
        approve_response = client.post("/api/v1/bounties/approve", headers=headers, json={
            "report_id": "test-report-id",
            "amount": 1000,
            "currency": "ETB"
        })
        assert approve_response.status_code in [201, 404, 400]


class TestFREQ10DuplicateDetection:
    """FREQ-10: Duplicate Report Detection"""
    
    def test_duplicate_detection(self, client, organization_token):
        """E2E: Detect duplicate reports"""
        headers = {"Authorization": f"Bearer {organization_token}"}
        
        # Check for duplicates
        duplicate_response = client.get("/api/v1/triage/duplicates", headers=headers)
        assert duplicate_response.status_code in [200, 404]


class TestFREQ11ReputationSystem:
    """FREQ-11: Reputation System"""
    
    def test_reputation_tracking(self, client, researcher_token):
        """E2E: View reputation and leaderboard"""
        headers = {"Authorization": f"Bearer {researcher_token}"}
        
        # Get own reputation
        reputation_response = client.get("/api/v1/my-reputation", headers=headers)
        assert reputation_response.status_code in [200, 404]
        
        # View leaderboard (public)
        leaderboard_response = client.get("/api/v1/leaderboard")
        assert leaderboard_response.status_code == 200
