"""
Integration Tests: Subscription Flow
Test subscription model with quarterly billing and commission
"""
import pytest


class TestSubscriptionFlow:
    """Test subscription and payment flow"""
    
    def test_subscription_tiers_available(self, client):
        """Test subscription tiers are available"""
        response = client.get("/api/v1/subscription/tiers")
        assert response.status_code == 200
        tiers = response.json()
        assert len(tiers) >= 3  # Basic, Professional, Enterprise
        
        # Verify tier structure
        for tier in tiers:
            assert "name" in tier
            assert "price" in tier
            assert "billing_cycle" in tier
    
    def test_organization_subscription(self, client, organization_token):
        """Test organization can subscribe to a tier"""
        headers = {"Authorization": f"Bearer {organization_token}"}
        
        # Subscribe to Professional tier
        subscription_data = {
            "tier": "professional",
            "billing_cycle": "quarterly"  # Every 4 months
        }
        response = client.post("/api/v1/subscription/subscribe", json=subscription_data, headers=headers)
        assert response.status_code == 201
        subscription = response.json()
        assert subscription["tier"] == "professional"
        assert subscription["status"] == "active"
        assert "next_billing_date" in subscription
    
    def test_subscription_status(self, client, organization_token):
        """Test organization can check subscription status"""
        headers = {"Authorization": f"Bearer {organization_token}"}
        response = client.get("/api/v1/subscription/status", headers=headers)
        assert response.status_code == 200
        status = response.json()
        assert "tier" in status
        assert "status" in status
        assert "next_billing_date" in status
    
    def test_commission_calculation(self, client, organization_token):
        """Test 30% commission is calculated correctly"""
        headers = {"Authorization": f"Bearer {organization_token}"}
        
        # Simulate bounty payment
        payment_data = {
            "researcher_amount": 1000,
            "currency": "ETB"
        }
        response = client.post("/api/v1/financial/calculate-commission", json=payment_data, headers=headers)
        assert response.status_code == 200
        calculation = response.json()
        
        # Verify commission calculation
        assert calculation["researcher_amount"] == 1000
        assert calculation["platform_commission"] == 300  # 30% of 1000
        assert calculation["total_amount"] == 1300  # 1000 + 300
        assert calculation["commission_rate"] == 0.30
    
    def test_billing_history(self, client, organization_token):
        """Test organization can view billing history"""
        headers = {"Authorization": f"Bearer {organization_token}"}
        response = client.get("/api/v1/financial/billing-history", headers=headers)
        assert response.status_code == 200
        history = response.json()
        assert isinstance(history, list) or "items" in history
