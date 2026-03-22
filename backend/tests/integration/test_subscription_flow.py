"""
Integration Tests for Subscription Flow
Tests the complete subscription lifecycle
"""
import pytest
from fastapi.testclient import TestClient


class TestSubscriptionFlow:
    """Test complete subscription workflow"""
    
    def test_organization_subscribe_basic_tier(self, client, organization_token):
        """Test organization subscribing to Basic tier"""
        headers = {"Authorization": f"Bearer {organization_token}"}
        
        # Subscribe to Basic tier
        response = client.post(
            "/api/v1/subscriptions/subscribe",
            headers=headers,
            json={
                "tier": "basic",
                "payment_method": "bank_transfer"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["tier"] == "basic"
        assert data["status"] == "active"
        assert "subscription_id" in data
    
    def test_organization_subscribe_professional_tier(self, client, organization_token):
        """Test organization subscribing to Professional tier"""
        headers = {"Authorization": f"Bearer {organization_token}"}
        
        response = client.post(
            "/api/v1/subscriptions/subscribe",
            headers=headers,
            json={
                "tier": "professional",
                "payment_method": "telebirr"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["tier"] == "professional"
        assert data["status"] == "active"
    
    def test_get_subscription_details(self, client, organization_token):
        """Test retrieving subscription details"""
        headers = {"Authorization": f"Bearer {organization_token}"}
        
        # First subscribe
        client.post(
            "/api/v1/subscriptions/subscribe",
            headers=headers,
            json={"tier": "basic", "payment_method": "bank_transfer"}
        )
        
        # Get subscription details
        response = client.get("/api/v1/subscriptions/current", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "tier" in data
        assert "status" in data
        assert "current_period_end" in data
    
    def test_upgrade_subscription(self, client, organization_token):
        """Test upgrading subscription tier"""
        headers = {"Authorization": f"Bearer {organization_token}"}
        
        # Subscribe to Basic
        client.post(
            "/api/v1/subscriptions/subscribe",
            headers=headers,
            json={"tier": "basic", "payment_method": "bank_transfer"}
        )
        
        # Upgrade to Professional
        response = client.post(
            "/api/v1/subscriptions/upgrade",
            headers=headers,
            json={"new_tier": "professional"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["tier"] == "professional"
    
    def test_cancel_subscription(self, client, organization_token):
        """Test canceling subscription"""
        headers = {"Authorization": f"Bearer {organization_token}"}
        
        # Subscribe first
        client.post(
            "/api/v1/subscriptions/subscribe",
            headers=headers,
            json={"tier": "basic", "payment_method": "bank_transfer"}
        )
        
        # Cancel subscription
        response = client.post("/api/v1/subscriptions/cancel", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["cancelled", "pending_cancellation"]
    
    def test_subscription_billing_history(self, client, organization_token):
        """Test retrieving billing history"""
        headers = {"Authorization": f"Bearer {organization_token}"}
        
        # Subscribe
        client.post(
            "/api/v1/subscriptions/subscribe",
            headers=headers,
            json={"tier": "professional", "payment_method": "telebirr"}
        )
        
        # Get billing history
        response = client.get("/api/v1/subscriptions/billing-history", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            assert "amount" in data[0]
            assert "payment_date" in data[0]
    
    def test_researcher_cannot_subscribe(self, client, researcher_token):
        """Test that researchers cannot subscribe (only organizations)"""
        headers = {"Authorization": f"Bearer {researcher_token}"}
        
        response = client.post(
            "/api/v1/subscriptions/subscribe",
            headers=headers,
            json={"tier": "basic", "payment_method": "bank_transfer"}
        )
        
        assert response.status_code == 403  # Forbidden
    
    def test_subscription_without_auth(self, client):
        """Test subscription endpoint without authentication"""
        response = client.post(
            "/api/v1/subscriptions/subscribe",
            json={"tier": "basic", "payment_method": "bank_transfer"}
        )
        
        assert response.status_code == 401  # Unauthorized


class TestBountyCommissionFlow:
    """Test bounty payment with commission"""
    
    def test_bounty_payment_with_commission(self, client, organization_token, researcher_token):
        """Test bounty payment includes 30% commission"""
        org_headers = {"Authorization": f"Bearer {organization_token}"}
        researcher_headers = {"Authorization": f"Bearer {researcher_token}"}
        
        # Organization creates program
        program_response = client.post(
            "/api/v1/programs",
            headers=org_headers,
            json={
                "name": "Test Program",
                "description": "Test bounty program",
                "scope": ["https://example.com"],
                "rewards": {"critical": 5000, "high": 3000}
            }
        )
        program_id = program_response.json()["id"]
        
        # Researcher submits report
        report_response = client.post(
            "/api/v1/reports",
            headers=researcher_headers,
            json={
                "program_id": program_id,
                "title": "Critical SQL Injection",
                "description": "SQL injection vulnerability",
                "severity": "critical",
                "vulnerability_type": "sqli",
                "steps_to_reproduce": "Test steps",
                "affected_url": "https://example.com/login"
            }
        )
        report_id = report_response.json()["id"]
        
        # Organization approves bounty
        bounty_response = client.post(
            f"/api/v1/bounties/{report_id}/approve",
            headers=org_headers,
            json={"amount": 1000}
        )
        
        assert bounty_response.status_code == 200
        data = bounty_response.json()
        
        # Check commission calculation
        assert data["researcher_amount"] == 1000
        assert data["platform_commission"] == 300  # 30%
        assert data["total_charge"] == 1300  # researcher + commission
