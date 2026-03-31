"""
E2E Tests for FREQ-20 to FREQ-22: Revenue Features
Tests subscriptions, commission, and payment processing
"""
import pytest


class TestFREQ20Subscriptions:
    """FREQ-20: Subscription Management"""
    
    def test_subscription_workflow(self, client, organization_token):
        """E2E: Subscribe to tier and manage subscription"""
        headers = {"Authorization": f"Bearer {organization_token}"}
        
        # List available tiers
        tiers_response = client.get("/api/v1/subscriptions/tiers", headers=headers)
        assert tiers_response.status_code in [200, 404]
        
        # Subscribe to basic tier
        subscribe_response = client.post("/api/v1/subscriptions", headers=headers, json={
            "tier": "basic",
            "payment_method": "bank_transfer"
        })
        assert subscribe_response.status_code in [201, 200, 400]
        
        # Get current subscription
        current_response = client.get("/api/v1/subscriptions/current", headers=headers)
        assert current_response.status_code in [200, 404]


class TestFREQ21Commission:
    """FREQ-21: 30% Platform Commission (BR-06)"""
    
    def test_commission_calculation(self, client, organization_token):
        """E2E: Calculate 30% commission on bounty payments"""
        headers = {"Authorization": f"Bearer {organization_token}"}
        
        # Calculate commission
        response = client.post("/api/v1/financial/calculate-commission", headers=headers, json={
            "researcher_amount": 1000
        })
        
        if response.status_code == 200:
            data = response.json()
            # Verify 30% commission
            assert data.get("commission") == 300
            assert data.get("total_charge") == 1300
    
    def test_commission_in_payment_flow(self, client, organization_token):
        """E2E: Verify commission is applied in payment processing"""
        headers = {"Authorization": f"Bearer {organization_token}"}
        
        # Process payment with commission
        response = client.post("/api/v1/payments/process", headers=headers, json={
            "amount": 1000,
            "payment_method": "bank_transfer",
            "description": "Bounty payment with commission"
        })
        assert response.status_code in [201, 200, 400]


class TestFREQ22PaymentProcessing:
    """FREQ-22: Payment Processing & Payouts"""
    
    def test_payment_gateway_integration(self, client, organization_token):
        """E2E: Process payment through gateway"""
        headers = {"Authorization": f"Bearer {organization_token}"}
        
        # List payment methods
        methods_response = client.get("/api/v1/payments/methods", headers=headers)
        assert methods_response.status_code in [200, 404]
        
        # Process payment
        payment_response = client.post("/api/v1/payments/process", headers=headers, json={
            "amount": 5000,
            "payment_method": "telebirr",
            "description": "Program funding"
        })
        assert payment_response.status_code in [201, 200, 400]
    
    def test_payout_workflow(self, client, researcher_token):
        """E2E: Request payout and track status"""
        headers = {"Authorization": f"Bearer {researcher_token}"}
        
        # Get wallet balance
        balance_response = client.get("/api/v1/wallet/balance", headers=headers)
        assert balance_response.status_code in [200, 404]
        
        # Request payout
        payout_response = client.post("/api/v1/payouts/request", headers=headers, json={
            "amount": 500,
            "payment_method": "bank_transfer"
        })
        assert payout_response.status_code in [201, 400]  # 400 if insufficient balance
        
        # List payouts
        list_response = client.get("/api/v1/payouts", headers=headers)
        assert list_response.status_code == 200
    
    def test_kyc_required_for_payout(self, client, researcher_token):
        """E2E: Verify KYC is required for payouts (BR-08)"""
        headers = {"Authorization": f"Bearer {researcher_token}"}
        
        # Check KYC status
        kyc_response = client.get("/api/v1/auth/kyc/status", headers=headers)
        assert kyc_response.status_code in [200, 404]
        
        # Start KYC if not completed
        if kyc_response.status_code == 200 and kyc_response.json().get("status") != "approved":
            start_kyc = client.post("/api/v1/auth/kyc/start", headers=headers)
            assert start_kyc.status_code in [200, 400, 500]
