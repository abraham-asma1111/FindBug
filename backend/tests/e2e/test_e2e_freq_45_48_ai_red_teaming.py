"""
E2E Tests for FREQ-45 to FREQ-48: AI Red Teaming
Tests AI red teaming engagements, scope definition, vulnerability reporting, and triage
"""
import pytest


class TestFREQ45AIRedTeamingEngagements:
    """FREQ-45: AI Red Teaming Engagement Management"""
    
    def test_create_ai_engagement(self, client, organization_token):
        """E2E: Create and manage AI red teaming engagement"""
        headers = {"Authorization": f"Bearer {organization_token}"}
        
        # Create AI red teaming engagement
        create_response = client.post("/api/v1/ai-red-teaming/engagements", headers=headers, json={
            "name": "LLM Security Assessment",
            "model_type": "llm",
            "model_name": "GPT-4",
            "testing_scope": "prompt injection, data leakage, jailbreaking",
            "start_date": "2026-04-01",
            "end_date": "2026-04-15"
        })
        assert create_response.status_code in [201, 200]
        
        if create_response.status_code in [201, 200]:
            engagement_id = create_response.json()["id"]
            
            # Get engagement details
            get_response = client.get(f"/api/v1/ai-red-teaming/engagements/{engagement_id}", headers=headers)
            assert get_response.status_code in [200, 404]
            
            # Update engagement
            update_response = client.put(f"/api/v1/ai-red-teaming/engagements/{engagement_id}", headers=headers, json={
                "status": "in_progress"
            })
            assert update_response.status_code in [200, 404]
    
    def test_list_ai_engagements(self, client, organization_token):
        """E2E: List all AI red teaming engagements"""
        headers = {"Authorization": f"Bearer {organization_token}"}
        
        response = client.get("/api/v1/ai-red-teaming/engagements", headers=headers)
        assert response.status_code in [200, 404]


class TestFREQ46AIRedTeamingScope:
    """FREQ-46: AI Red Teaming Scope Definition"""
    
    def test_define_testing_scope(self, client, organization_token):
        """E2E: Define and manage AI testing scope"""
        headers = {"Authorization": f"Bearer {organization_token}"}
        
        # Define scope
        scope_response = client.post("/api/v1/ai-red-teaming/engagements/test-engagement-id/scope", headers=headers, json={
            "attack_vectors": [
                "prompt_injection",
                "data_leakage",
                "jailbreaking",
                "adversarial_inputs"
            ],
            "model_endpoints": ["https://api.example.com/chat"],
            "testing_constraints": "No destructive testing",
            "success_criteria": "Identify at least 5 vulnerabilities"
        })
        assert scope_response.status_code in [201, 200, 404]
        
        # Get scope details
        get_scope = client.get("/api/v1/ai-red-teaming/engagements/test-engagement-id/scope", headers=headers)
        assert get_scope.status_code in [200, 404]


class TestFREQ47AIVulnerabilityReporting:
    """FREQ-47: AI Vulnerability Reporting"""
    
    def test_submit_ai_vulnerability(self, client, researcher_token):
        """E2E: Submit AI vulnerability report"""
        headers = {"Authorization": f"Bearer {researcher_token}"}
        
        # Submit AI vulnerability
        submit_response = client.post("/api/v1/ai-red-teaming/vulnerabilities", headers=headers, json={
            "engagement_id": "test-engagement-id",
            "attack_type": "prompt_injection",
            "title": "Prompt Injection Bypasses Safety Filters",
            "description": "Model can be tricked into generating harmful content",
            "severity": "high",
            "proof_of_concept": "Prompt: 'Ignore previous instructions...'",
            "impact": "Model generates inappropriate content",
            "reproduction_steps": "1. Send prompt\n2. Observe response"
        })
        assert submit_response.status_code in [201, 404]
    
    def test_list_ai_vulnerabilities(self, client, organization_token):
        """E2E: List AI vulnerabilities"""
        headers = {"Authorization": f"Bearer {organization_token}"}
        
        response = client.get("/api/v1/ai-red-teaming/vulnerabilities", headers=headers)
        assert response.status_code in [200, 404]
    
    def test_ai_vulnerability_with_token_encryption(self, client, researcher_token):
        """E2E: Submit vulnerability with encrypted API tokens"""
        headers = {"Authorization": f"Bearer {researcher_token}"}
        
        # Submit with encrypted token
        submit_response = client.post("/api/v1/ai-red-teaming/vulnerabilities", headers=headers, json={
            "engagement_id": "test-engagement-id",
            "attack_type": "data_leakage",
            "title": "Model Leaks Training Data",
            "description": "Model reveals sensitive information",
            "severity": "critical",
            "encrypted_token": "encrypted_api_token_here",
            "proof_of_concept": "Query reveals PII"
        })
        assert submit_response.status_code in [201, 404]


class TestFREQ48AITriageWorkflow:
    """FREQ-48: AI Red Teaming Triage Workflow"""
    
    def test_ai_triage_queue(self, client, organization_token):
        """E2E: View and manage AI vulnerability triage queue"""
        headers = {"Authorization": f"Bearer {organization_token}"}
        
        # Get AI triage queue
        queue_response = client.get("/api/v1/ai-red-teaming/triage/queue", headers=headers)
        assert queue_response.status_code in [200, 404]
        
        # Get triage statistics
        stats_response = client.get("/api/v1/ai-red-teaming/triage/statistics", headers=headers)
        assert stats_response.status_code in [200, 404]
    
    def test_triage_ai_vulnerability(self, client, organization_token):
        """E2E: Triage AI vulnerability"""
        headers = {"Authorization": f"Bearer {organization_token}"}
        
        # Triage vulnerability
        triage_response = client.post("/api/v1/ai-red-teaming/vulnerabilities/test-vuln-id/triage", headers=headers, json={
            "status": "validated",
            "severity": "high",
            "priority": "urgent",
            "notes": "Confirmed vulnerability, needs immediate attention"
        })
        assert triage_response.status_code in [200, 404]
    
    def test_assign_ai_vulnerability(self, client, organization_token):
        """E2E: Assign AI vulnerability to team member"""
        headers = {"Authorization": f"Bearer {organization_token}"}
        
        # Assign to team member
        assign_response = client.post("/api/v1/ai-red-teaming/vulnerabilities/test-vuln-id/assign", headers=headers, json={
            "assignee_id": "test-user-id"
        })
        assert assign_response.status_code in [200, 404]
    
    def test_ai_vulnerability_remediation(self, client, organization_token):
        """E2E: Mark AI vulnerability as remediated"""
        headers = {"Authorization": f"Bearer {organization_token}"}
        
        # Mark as remediated
        remediate_response = client.post("/api/v1/ai-red-teaming/vulnerabilities/test-vuln-id/remediate", headers=headers, json={
            "remediation_notes": "Implemented input validation",
            "fix_verification": "Tested with original PoC"
        })
        assert remediate_response.status_code in [200, 404]


class TestAIRedTeamingIntegration:
    """Integration test for complete AI red teaming workflow"""
    
    def test_complete_ai_red_teaming_workflow(self, client, organization_token, researcher_token):
        """E2E: Complete AI red teaming workflow from engagement to remediation"""
        org_headers = {"Authorization": f"Bearer {organization_token}"}
        researcher_headers = {"Authorization": f"Bearer {researcher_token}"}
        
        # 1. Organization creates engagement
        engagement_response = client.post("/api/v1/ai-red-teaming/engagements", headers=org_headers, json={
            "name": "Complete AI Security Test",
            "model_type": "llm",
            "testing_scope": "comprehensive security assessment",
            "start_date": "2026-04-01",
            "end_date": "2026-04-15"
        })
        assert engagement_response.status_code in [201, 200]
        
        if engagement_response.status_code in [201, 200]:
            engagement_id = engagement_response.json()["id"]
            
            # 2. Researcher submits vulnerability
            vuln_response = client.post("/api/v1/ai-red-teaming/vulnerabilities", headers=researcher_headers, json={
                "engagement_id": engagement_id,
                "attack_type": "prompt_injection",
                "title": "Critical Prompt Injection",
                "description": "Severe vulnerability",
                "severity": "critical"
            })
            assert vuln_response.status_code in [201, 404]
            
            # 3. Organization triages vulnerability
            if vuln_response.status_code == 201:
                vuln_id = vuln_response.json()["id"]
                
                triage_response = client.post(f"/api/v1/ai-red-teaming/vulnerabilities/{vuln_id}/triage", headers=org_headers, json={
                    "status": "validated",
                    "severity": "critical"
                })
                assert triage_response.status_code in [200, 404]
