"""
Test script to verify wallet and KYC fixes.

Run this after starting the backend:
    cd backend
    docker-compose up -d
    python test_wallet_kyc_fix.py
"""
import requests
import json

BASE_URL = "http://localhost:8002"

# Test user credentials (sakox12713@justnapa.com)
TEST_EMAIL = "sakox12713@justnapa.com"
TEST_PASSWORD = "Test123!@#"

def login():
    """Login and get access token"""
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Login successful")
        print(f"   User ID: {data.get('user_id')}")
        print(f"   Role: {data.get('role')}")
        return data.get("access_token")
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return None

def test_wallet_balance(token):
    """Test wallet balance endpoint"""
    print("\n" + "="*60)
    print("TEST 1: Wallet Balance")
    print("="*60)
    
    response = requests.get(
        f"{BASE_URL}/api/v1/wallet/balance",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Wallet balance retrieved successfully")
        print(f"   Wallet ID: {data.get('wallet_id')}")
        print(f"   Balance: {data.get('balance')} {data.get('currency')}")
        print(f"   Available: {data.get('available_balance')} {data.get('currency')}")
        print(f"   Reserved: {data.get('reserved_balance')} {data.get('currency')}")
    else:
        print(f"❌ Wallet balance failed")
        print(f"   Response: {response.text}")

def test_persona_status(token):
    """Test Persona KYC status endpoint"""
    print("\n" + "="*60)
    print("TEST 2: Persona KYC Status")
    print("="*60)
    
    response = requests.get(
        f"{BASE_URL}/api/v1/kyc/persona/status",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Persona status retrieved successfully")
        print(f"   Status: {data.get('status')}")
        print(f"   Persona Status: {data.get('persona_status')}")
        print(f"   Inquiry ID: {data.get('persona_inquiry_id')}")
        print(f"   Email Verified: {data.get('email_verified')}")
        print(f"   Can Verify Email: {data.get('can_verify_email')}")
    else:
        print(f"❌ Persona status failed")
        print(f"   Response: {response.text}")

def test_email_status(token):
    """Test Email verification status endpoint"""
    print("\n" + "="*60)
    print("TEST 3: Email Verification Status")
    print("="*60)
    
    response = requests.get(
        f"{BASE_URL}/api/v1/kyc/email/status",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Email status retrieved successfully")
        print(f"   Email Verified: {data.get('email_verified')}")
        print(f"   Email Address: {data.get('email_address')}")
        print(f"   Can Verify Email: {data.get('can_verify_email')}")
    else:
        print(f"❌ Email status failed")
        print(f"   Response: {response.text}")

def main():
    print("="*60)
    print("WALLET & KYC FIX VERIFICATION TEST")
    print("="*60)
    print(f"Backend URL: {BASE_URL}")
    print(f"Test User: {TEST_EMAIL}")
    
    # Login
    token = login()
    if not token:
        print("\n❌ Cannot proceed without authentication token")
        return
    
    # Test wallet balance (should work now with user_id fix)
    test_wallet_balance(token)
    
    # Test Persona status
    test_persona_status(token)
    
    # Test Email status
    test_email_status(token)
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print("Expected Results:")
    print("  1. Wallet balance should return 200 OK (not 500)")
    print("  2. Persona status should return valid JSON (not null)")
    print("  3. Email status should return valid JSON (not null)")
    print("="*60)

if __name__ == "__main__":
    main()
