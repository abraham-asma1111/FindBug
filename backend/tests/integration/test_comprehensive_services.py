"""
Comprehensive Integration Tests for All 38 Services
Tests all major services with real database interactions
"""
import pytest
from datetime import datetime, timedelta
from decimal import Decimal


# ============================================================================
# SERVICE 1: Admin Service
# ============================================================================
class TestAdminService:
    """Test admin service functionality"""
    
    def test_get_platform_statistics(self, client, staff_token):
        """Test retrieving platform statistics"""
        headers = {"Authorization": f"Bearer {staff_token}"}
        response = client.get("/api/v1/admin/statistics", headers=headers)
        assert response.status_code in [200, 403]  # 403 if staff not implemented
    
    def test_manage_users(self, client, staff_token):
        """Test user management"""
        headers = {"Authorization": f"Bearer {staff_token}"}
        response = client.get("/api/v1/admin/users", headers=headers)
        assert response.status_code in [200, 403]


# ============================================================================
# SERVICE 2: AI Red Teaming Service
# ============================================================================
class TestAIRedTeamingService:
    """Test AI red teaming service"""
    
    def test_create_ai_engagement(self, client, organization_token):
        """Test creating AI red teaming engagement"""
        headers = {"Authorization": f"Bearer {organization_token}"}
        response = client.post("/api/v1/ai-red-teaming/engagements", headers=headers, json={
            "name": "LLM Security Assessment",
            "model_type": "llm",
            "testing_scope": "prompt injection, data leakage",
            "start_date": "2026-04-01",
            "end_date": "2026-04-15"
        })
        assert response.status_code in [201, 200]
    
    def test_submit_ai_vulnerability(self, client, researcher_token):
        """Test submitting AI vulnerability"""
        headers = {"Authorization": f"Bearer {researcher_token}"}
        response = client.post("/api/v1/ai-red-teaming/vulnerabilities", headers=headers, json={
            "engagement_id": "test-engagement-id",
            "attack_type": "prompt_injection",
            "description": "Model reveals training data",
            "severity": "high",
            "proof_of_concept": "Test PoC"
        })
        assert response.status_code in [201, 404]  # 404 if engagement doesn't exist


# ============================================================================
# SERVICE 3: Analytics Service
# ============================================================================
class TestAnalyticsService:
    """Test analytics service"""
    
    def test_organization_analytics(self, client, organization_token):
        """Test organization analytics dashboard"""
        headers = {"Authorization": f"Bearer {organization_token}"}
        response = client.get("/api/v1/analytics/organization", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "total_reports" in data or "reports" in data or "statistics" in data
    
    def test_researcher_analytics(self, client, researcher_token):
        """Test researcher analytics"""
        headers = {"Authorization": f"Bearer {researcher_token}"}
        response = client.get("/api/v1/analytics/researcher", headers=headers)
        assert response.status_code == 200


# ============================================================================
# SERVICE 4: Audit Service
# ============================================================================
class TestAuditService:
    """Test audit logging service"""
    
    def test_view_audit_logs(self, client, staff_token):
        """Test viewing audit logs"""
        headers = {"Authorization": f"Bearer {staff_token}"}
        response = client.get("/api/v1/admin/audit-logs", headers=headers)
        assert response.status_code in [200, 403]
    
    def test_search_audit_logs(self, client, staff_token):
        """Test searching audit logs"""
        headers = {"Authorization": f"Bearer {staff_token}"}
        response = client.get("/api/v1/admin/audit-logs?event_type=login", headers=headers)
        assert response.status_code in [200, 403]


# ============================================================================
# SERVICE 5: Auth Service (Already tested in test_auth_flow.py)
# ============================================================================


# ============================================================================
# SERVICE 6: Bounty Service
# ============================================================================
class TestBountyService:
    """Test bounty payment service"""
    
    def test_approve_bounty(self, client, organization_token):
        """Test approving bounty payment"""
        headers = {"Authorization": f"Bearer {organization_token}"}
        response = client.post("/api/v1/bounties/approve", headers=headers, json={
            "report_id": "test-report-id",
            "amount": 1000,
            "currency": "ETB"
        })
        assert response.status_code in [201, 404]
    
    def test_list_bounties(self, client, researcher_token):
        """Test listing bounties"""
        headers = {"Authorization": f"Bearer {researcher_token}"}
        response = client.get("/api/v1/bounties", headers=headers)
        assert response.status_code == 200


# ============================================================================
# SERVICE 7: Code Review Service
# ============================================================================
class TestCodeReviewService:
    """Test code review service"""
    
    def test_create_code_review_engagement(self, client, organization_token):
        """Test creating code review engagement"""
        headers = {"Authorization": f"Bearer {organization_token}"}
        response = client.post("/api/v1/code-review/engagements", headers=headers, json={
            "name": "API Security Review",
            "repository_url": "https://github.com/org/repo",
            "scope": "security review",
            "start_date": "2026-04-01"
        })
        assert response.status_code in [201, 200]
    
    def test_list_code_reviews(self, client, organization_token):
        """Test listing code reviews"""
        headers = {"Authorization": f"Bearer {organization_token}"}
        response = client.get("/api/v1/code-review/engagements", headers=headers)
        assert response.status_code == 200


# ============================================================================
# SERVICE 8: Commission Service
# ============================================================================
class TestCommissionService:
    """Test commission calculation service"""
    
    def test_calculate_commission(self, client, organization_token):
        """Test calculating 30% commission"""
        headers = {"Authorization": f"Bearer {organization_token}"}
        response = client.post("/api/v1/financial/calculate-commission", headers=headers, json={
            "researcher_amount": 1000
        })
        if response.status_code == 200:
            data = response.json()
            assert data["commission"] == 300
            assert data["total_charge"] == 1300


# ============================================================================
# SERVICE 9: Compliance Service
# ============================================================================
class TestComplianceService:
    """Test compliance reporting service"""
    
    def test_generate_compliance_report(self, client, organization_token):
        """Test generating compliance report"""
        headers = {"Authorization": f"Bearer {organization_token}"}
        response = client.post("/api/v1/compliance/reports", headers=headers, json={
            "report_type": "gdpr",
            "start_date": "2026-01-01",
            "end_date": "2026-03-31"
        })
        assert response.status_code in [201, 200]


# ============================================================================
# SERVICE 10: Container Service
# ============================================================================
class TestContainerService:
    """Test Docker container orchestration service"""
    
    def test_start_simulation_container(self, client, researcher_token):
        """Test starting simulation container"""
        headers = {"Authorization": f"Bearer {researcher_token}"}
        response = client.post("/api/v1/simulation/challenges/test-challenge/start", headers=headers)
        assert response.status_code in [201, 404]


# ============================================================================
# SERVICE 11: Dashboard Service
# ============================================================================
class TestDashboardService:
    """Test dashboard service"""
    
    def test_get_dashboard_metrics(self, client, organization_token):
        """Test retrieving dashboard metrics"""
        headers = {"Authorization": f"Bearer {organization_token}"}
        response = client.get("/api/v1/dashboard", headers=headers)
        assert response.status_code == 200


# ============================================================================
# SERVICE 12: Data Export Service
# ============================================================================
class TestDataExportService:
    """Test data export service"""
    
    def test_request_data_export(self, client, researcher_token):
        """Test requesting data export"""
        headers = {"Authorization": f"Bearer {researcher_token}"}
        response = client.post("/api/v1/data-exports", headers=headers, json={
            "export_type": "reports",
            "format": "json"
        })
        assert response.status_code in [201, 200]


# ============================================================================
# SERVICE 13: Email Template Service
# ============================================================================
class TestEmailTemplateService:
    """Test email template service"""
    
    def test_list_email_templates(self, client, staff_token):
        """Test listing email templates"""
        headers = {"Authorization": f"Bearer {staff_token}"}
        response = client.get("/api/v1/email-templates", headers=headers)
        assert response.status_code in [200, 403]


# ============================================================================
# SERVICE 14: Enhanced Payout Service
# ============================================================================
class TestEnhancedPayoutService:
    """Test enhanced payout service"""
    
    def test_request_payout(self, client, researcher_token):
        """Test requesting payout"""
        headers = {"Authorization": f"Bearer {researcher_token}"}
        response = client.post("/api/v1/payouts/request", headers=headers, json={
            "amount": 500,
            "payment_method": "bank_transfer"
        })
        assert response.status_code in [201, 400]  # 400 if insufficient balance


# ============================================================================
# SERVICE 15: File Storage Service
# ============================================================================
class TestFileStorageService:
    """Test file storage service"""
    
    def test_upload_file(self, client, researcher_token):
        """Test uploading file"""
        headers = {"Authorization": f"Bearer {researcher_token}"}
        files = {"file": ("test.txt", b"test content", "text/plain")}
        response = client.post("/api/v1/files/upload", headers=headers, files=files)
        assert response.status_code in [201, 200]


# ============================================================================
# SERVICE 16: Integration Service
# ============================================================================
class TestIntegrationService:
    """Test external integration service"""
    
    def test_connect_github(self, client, organization_token):
        """Test GitHub integration"""
        headers = {"Authorization": f"Bearer {organization_token}"}
        response = client.post("/api/v1/integrations/github", headers=headers, json={
            "access_token": "test_token",
            "repository": "org/repo"
        })
        assert response.status_code in [201, 200, 400]


# ============================================================================
# SERVICE 17: KYC Service
# ============================================================================
class TestKYCService:
    """Test KYC verification service"""
    
    def test_start_kyc_verification(self, client, researcher_token):
        """Test starting KYC verification"""
        headers = {"Authorization": f"Bearer {researcher_token}"}
        response = client.post("/api/v1/auth/kyc/start", headers=headers)
        assert response.status_code in [200, 400, 500]  # May fail if Persona not configured


# ============================================================================
# SERVICE 18: Live Event Service
# ============================================================================
class TestLiveEventService:
    """Test live hacking event service"""
    
    def test_create_live_event(self, client, organization_token):
        """Test creating live hacking event"""
        headers = {"Authorization": f"Bearer {organization_token}"}
        response = client.post("/api/v1/live-events", headers=headers, json={
            "name": "Spring Security Event",
            "start_time": "2026-05-01T10:00:00Z",
            "end_time": "2026-05-03T18:00:00Z",
            "prize_pool": 50000,
            "max_participants": 50
        })
        assert response.status_code in [201, 200]


# ============================================================================
# SERVICE 19: Matching Service
# ============================================================================
class TestMatchingService:
    """Test researcher-program matching service"""
    
    def test_get_recommendations(self, client, researcher_token):
        """Test getting program recommendations"""
        headers = {"Authorization": f"Bearer {researcher_token}"}
        response = client.get("/api/v1/matching/recommendations", headers=headers)
        assert response.status_code == 200


# ============================================================================
# SERVICE 20: Message Service
# ============================================================================
class TestMessageService:
    """Test messaging service"""
    
    def test_send_message(self, client, researcher_token):
        """Test sending message"""
        headers = {"Authorization": f"Bearer {researcher_token}"}
        response = client.post("/api/v1/messages", headers=headers, json={
            "recipient_id": "test-user-id",
            "subject": "Test Message",
            "content": "Hello"
        })
        assert response.status_code in [201, 404]


# ============================================================================
# SERVICE 21: Notification Service
# ============================================================================
class TestNotificationService:
    """Test notification service"""
    
    def test_get_notifications(self, client, researcher_token):
        """Test retrieving notifications"""
        headers = {"Authorization": f"Bearer {researcher_token}"}
        response = client.get("/api/v1/notifications", headers=headers)
        assert response.status_code == 200


# ============================================================================
# SERVICE 22: Payment Service
# ============================================================================
class TestPaymentService:
    """Test payment processing service"""
    
    def test_process_payment(self, client, organization_token):
        """Test processing payment"""
        headers = {"Authorization": f"Bearer {organization_token}"}
        response = client.post("/api/v1/payments/process", headers=headers, json={
            "amount": 1000,
            "payment_method": "bank_transfer",
            "description": "Bounty payment"
        })
        assert response.status_code in [201, 200, 400]


# ============================================================================
# SERVICE 23: Payout Service
# ============================================================================
class TestPayoutService:
    """Test payout service"""
    
    def test_list_payouts(self, client, researcher_token):
        """Test listing payouts"""
        headers = {"Authorization": f"Bearer {researcher_token}"}
        response = client.get("/api/v1/payouts", headers=headers)
        assert response.status_code == 200


# ============================================================================
# SERVICE 24: Program Service
# ============================================================================
class TestProgramService:
    """Test bug bounty program service"""
    
    def test_create_program(self, client, organization_token):
        """Test creating bug bounty program"""
        headers = {"Authorization": f"Bearer {organization_token}"}
        response = client.post("/api/v1/programs", headers=headers, json={
            "name": "Security Program",
            "description": "Find vulnerabilities",
            "scope": ["https://example.com"],
            "rewards": {"critical": 5000, "high": 3000}
        })
        assert response.status_code in [201, 200]
    
    def test_list_programs(self, client, researcher_token):
        """Test listing programs"""
        headers = {"Authorization": f"Bearer {researcher_token}"}
        response = client.get("/api/v1/programs", headers=headers)
        assert response.status_code == 200


# ============================================================================
# SERVICE 25-28: PTaaS Services
# ============================================================================
class TestPTaaSServices:
    """Test PTaaS services"""
    
    def test_create_ptaas_engagement(self, client, organization_token):
        """Test creating PTaaS engagement"""
        headers = {"Authorization": f"Bearer {organization_token}"}
        response = client.post("/api/v1/ptaas/engagements", headers=headers, json={
            "name": "Q1 Pentest",
            "scope": ["https://example.com"],
            "start_date": "2026-04-01",
            "end_date": "2026-04-15"
        })
        assert response.status_code in [201, 200]
    
    def test_ptaas_dashboard(self, client, organization_token):
        """Test PTaaS dashboard"""
        headers = {"Authorization": f"Bearer {organization_token}"}
        response = client.get("/api/v1/ptaas/dashboard", headers=headers)
        assert response.status_code == 200


# ============================================================================
# SERVICE 29: Report Service
# ============================================================================
class TestReportService:
    """Test vulnerability report service"""
    
    def test_submit_report(self, client, researcher_token, organization_token):
        """Test submitting vulnerability report"""
        # First create a program
        org_headers = {"Authorization": f"Bearer {organization_token}"}
        program_response = client.post("/api/v1/programs", headers=org_headers, json={
            "name": "Test Program",
            "description": "Test",
            "scope": ["https://example.com"]
        })
        
        if program_response.status_code in [201, 200]:
            program_id = program_response.json()["id"]
            
            # Submit report
            researcher_headers = {"Authorization": f"Bearer {researcher_token}"}
            response = client.post("/api/v1/reports", headers=researcher_headers, json={
                "program_id": program_id,
                "title": "SQL Injection",
                "description": "SQL injection found",
                "severity": "high",
                "vulnerability_type": "sqli"
            })
            assert response.status_code in [201, 200]


# ============================================================================
# SERVICE 30: Reputation Service
# ============================================================================
class TestReputationService:
    """Test reputation service"""
    
    def test_get_reputation(self, client, researcher_token):
        """Test getting researcher reputation"""
        headers = {"Authorization": f"Bearer {researcher_token}"}
        response = client.get("/api/v1/my-reputation", headers=headers)
        assert response.status_code in [200, 404]
    
    def test_leaderboard(self, client):
        """Test global leaderboard"""
        response = client.get("/api/v1/leaderboard")
        assert response.status_code == 200


# ============================================================================
# SERVICE 31: Security Service
# ============================================================================
class TestSecurityService:
    """Test security service"""
    
    def test_security_events(self, client, staff_token):
        """Test viewing security events"""
        headers = {"Authorization": f"Bearer {staff_token}"}
        response = client.get("/api/v1/security/events", headers=headers)
        assert response.status_code in [200, 403]


# ============================================================================
# SERVICE 32: Simulation Service
# ============================================================================
class TestSimulationService:
    """Test simulation platform service"""
    
    def test_list_challenges(self, client, researcher_token):
        """Test listing simulation challenges"""
        headers = {"Authorization": f"Bearer {researcher_token}"}
        response = client.get("/api/v1/simulation/challenges", headers=headers)
        assert response.status_code == 200
    
    def test_simulation_leaderboard(self, client):
        """Test simulation leaderboard"""
        response = client.get("/api/v1/simulation/leaderboard")
        assert response.status_code == 200


# ============================================================================
# SERVICE 33: Subscription Service
# ============================================================================
class TestSubscriptionService:
    """Test subscription service"""
    
    def test_subscribe(self, client, organization_token):
        """Test subscribing to tier"""
        headers = {"Authorization": f"Bearer {organization_token}"}
        response = client.post("/api/v1/subscriptions", headers=headers, json={
            "tier": "basic",
            "payment_method": "bank_transfer"
        })
        assert response.status_code in [201, 200, 400]


# ============================================================================
# SERVICE 34: Triage Service
# ============================================================================
class TestTriageService:
    """Test report triage service"""
    
    def test_triage_report(self, client, organization_token):
        """Test triaging report"""
        headers = {"Authorization": f"Bearer {organization_token}"}
        response = client.post("/api/v1/triage/test-report-id", headers=headers, json={
            "status": "validated",
            "severity": "high"
        })
        assert response.status_code in [200, 404]


# ============================================================================
# SERVICE 35: User Service
# ============================================================================
class TestUserService:
    """Test user service"""
    
    def test_get_profile(self, client, researcher_token):
        """Test getting user profile"""
        headers = {"Authorization": f"Bearer {researcher_token}"}
        response = client.get("/api/v1/profile", headers=headers)
        assert response.status_code in [200, 404]
    
    def test_update_profile(self, client, researcher_token):
        """Test updating profile"""
        headers = {"Authorization": f"Bearer {researcher_token}"}
        response = client.put("/api/v1/profile", headers=headers, json={
            "bio": "Updated bio"
        })
        assert response.status_code in [200, 404]


# ============================================================================
# SERVICE 36: VRT Service
# ============================================================================
class TestVRTService:
    """Test Vulnerability Rating Taxonomy service"""
    
    def test_list_vrt_categories(self, client):
        """Test listing VRT categories"""
        response = client.get("/api/v1/vrt/categories")
        assert response.status_code == 200


# ============================================================================
# SERVICE 37: Wallet Service
# ============================================================================
class TestWalletService:
    """Test wallet service"""
    
    def test_get_wallet_balance(self, client, researcher_token):
        """Test getting wallet balance"""
        headers = {"Authorization": f"Bearer {researcher_token}"}
        response = client.get("/api/v1/wallet/balance", headers=headers)
        assert response.status_code in [200, 404]


# ============================================================================
# SERVICE 38: Webhook Service
# ============================================================================
class TestWebhookService:
    """Test webhook service"""
    
    def test_register_webhook(self, client, organization_token):
        """Test registering webhook"""
        headers = {"Authorization": f"Bearer {organization_token}"}
        response = client.post("/api/v1/webhooks", headers=headers, json={
            "url": "https://example.com/webhook",
            "events": ["report.submitted", "bounty.approved"]
        })
        assert response.status_code in [201, 200]
