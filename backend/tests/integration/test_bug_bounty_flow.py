"""
Integration Tests: Bug Bounty Flow
Test complete bug bounty workflow from program creation to payment
"""
import pytest


class TestBugBountyFlow:
    """Test complete bug bounty workflow"""
    
    def test_complete_bug_bounty_flow(self, client, organization_token, researcher_token, staff_token):
        """Test full bug bounty flow: create program → submit report → triage → approve → pay"""
        
        # Step 1: Organization creates a program
        org_headers = {"Authorization": f"Bearer {organization_token}"}
        program_data = {
            "name": "Test Bug Bounty Program",
            "description": "Test program for integration testing",
            "scope": ["https://test.example.com"],
            "rewards": {
                "critical": 5000,
                "high": 2000,
                "medium": 500,
                "low": 100
            },
            "is_public": True
        }
        response = client.post("/api/v1/programs", json=program_data, headers=org_headers)
        assert response.status_code == 201
        program = response.json()
        program_id = program["id"]
        
        # Step 2: Researcher submits a vulnerability report
        researcher_headers = {"Authorization": f"Bearer {researcher_token}"}
        report_data = {
            "program_id": program_id,
            "title": "SQL Injection in Login Form",
            "description": "Found SQL injection vulnerability",
            "steps_to_reproduce": "1. Go to login\n2. Enter ' OR '1'='1\n3. Bypass authentication",
            "impact": "Complete database compromise",
            "severity": "critical",
            "proof_of_concept": "Screenshot attached"
        }
        response = client.post("/api/v1/reports", json=report_data, headers=researcher_headers)
        assert response.status_code == 201
        report = response.json()
        report_id = report["id"]
        assert report["status"] == "submitted"
        
        # Step 3: Staff triages the report
        staff_headers = {"Authorization": f"Bearer {staff_token}"}
        triage_data = {
            "status": "valid",
            "severity": "critical",
            "notes": "Confirmed SQL injection vulnerability"
        }
        response = client.patch(f"/api/v1/triage/{report_id}", json=triage_data, headers=staff_headers)
        assert response.status_code == 200
        
        # Step 4: Organization approves bounty payment
        bounty_data = {
            "report_id": report_id,
            "amount": 5000,
            "currency": "ETB"
        }
        response = client.post("/api/v1/bounty/approve", json=bounty_data, headers=org_headers)
        assert response.status_code == 200
        
        # Step 5: Verify payment was processed (30% commission model)
        response = client.get(f"/api/v1/financial/payments/{report_id}", headers=org_headers)
        assert response.status_code == 200
        payment = response.json()
        assert payment["researcher_amount"] == 5000
        assert payment["platform_commission"] == 1500  # 30% of 5000
        assert payment["total_amount"] == 6500  # 5000 + 1500
    
    def test_program_listing(self, client, researcher_token):
        """Test researcher can view public programs"""
        headers = {"Authorization": f"Bearer {researcher_token}"}
        response = client.get("/api/v1/programs", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list) or "items" in data
    
    def test_report_submission_validation(self, client, researcher_token):
        """Test report submission with invalid data fails"""
        headers = {"Authorization": f"Bearer {researcher_token}"}
        invalid_report = {
            "title": "Test",
            # Missing required fields
        }
        response = client.post("/api/v1/reports", json=invalid_report, headers=headers)
        assert response.status_code == 422  # Validation error
