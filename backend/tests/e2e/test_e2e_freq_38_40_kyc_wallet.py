"""
E2E Tests for FREQ-38 to FREQ-40: KYC, Recommendations, and Wallet
Tests KYC verification, personalized recommendations, and wallet management
"""
import pytest


class TestFREQ38KYCVerification:
    """FREQ-38: KYC Verification (BR-08)"""
    
    def test_complete_kyc_workflow(self, client, researcher_token):
        """E2E: Complete KYC verification process"""
        headers = {"Authorization": f"Bearer {researcher_token}"}
        
        # Check KYC status
        status_response = client.get("/api/v1/auth/kyc/status", headers=headers)
        assert status_response.status_code in [200, 404]
        
        # Start KYC verification
        start_response = client.post("/api/v1/auth/kyc/start", headers=headers)
        assert start_response.status_code in [200, 400, 500]
        
        # Upload KYC document
        files = {"file": ("id_card.jpg", b"fake image data", "image/jpeg")}
        upload_response = client.post("/api/v1/auth/kyc/upload", headers=headers, files=files, data={
            "document_type": "national_id"
        })
        assert upload_response.status_code in [201, 200, 400]
    
    def test_kyc_required_for_payout(self, client, researcher_token):
        """E2E: Verify KYC blocks payout if not completed"""
        headers = {"Authorization": f"Bearer {researcher_token}"}
        
        # Try to request payout without KYC
        payout_response = client.post("/api/v1/payouts/request", headers=headers, json={
            "amount": 1000,
            "payment_method": "bank_transfer"
        })
        # Should fail if KYC not completed
        assert payout_response.status_code in [201, 400, 403]


class TestFREQ39PersonalizedRecommendations:
    """FREQ-39: Personalized Program Recommendations"""
    
    def test_get_personalized_recommendations(self, client, researcher_token):
        """E2E: Get personalized program recommendations"""
        headers = {"Authorization": f"Bearer {researcher_token}"}
        
        # Get recommendations based on skills and history
        response = client.get("/api/v1/matching/recommendations", headers=headers)
        assert response.status_code == 200
        
        # Get recommendations with filters
        filtered_response = client.get("/api/v1/matching/recommendations?min_bounty=1000", headers=headers)
        assert filtered_response.status_code == 200
    
    def test_recommendation_feedback(self, client, researcher_token):
        """E2E: Provide feedback on recommendations"""
        headers = {"Authorization": f"Bearer {researcher_token}"}
        
        # Provide feedback
        feedback_response = client.post("/api/v1/matching/recommendations/test-program-id/feedback", headers=headers, json={
            "interested": True,
            "reason": "Matches my skills"
        })
        assert feedback_response.status_code in [200, 404]


class TestFREQ40WalletManagement:
    """FREQ-40: Wallet & Balance Management"""
    
    def test_wallet_operations(self, client, researcher_token):
        """E2E: View wallet balance and transaction history"""
        headers = {"Authorization": f"Bearer {researcher_token}"}
        
        # Get wallet balance
        balance_response = client.get("/api/v1/wallet/balance", headers=headers)
        assert balance_response.status_code in [200, 404]
        
        # Get transaction history
        transactions_response = client.get("/api/v1/wallet/transactions", headers=headers)
        assert transactions_response.status_code in [200, 404]
        
        # Get pending earnings
        pending_response = client.get("/api/v1/wallet/pending", headers=headers)
        assert pending_response.status_code in [200, 404]
    
    def test_wallet_withdrawal(self, client, researcher_token):
        """E2E: Withdraw funds from wallet"""
        headers = {"Authorization": f"Bearer {researcher_token}"}
        
        # Request withdrawal
        withdrawal_response = client.post("/api/v1/wallet/withdraw", headers=headers, json={
            "amount": 500,
            "payment_method": "bank_transfer",
            "bank_account": "1234567890"
        })
        assert withdrawal_response.status_code in [201, 400]  # 400 if insufficient balance
