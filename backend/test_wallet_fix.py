"""
Test script to verify wallet endpoint 403 fix.
"""
import requests
import sys

# Get auth token for test researcher user
def get_auth_token():
    """Login as test researcher and get token."""
    login_url = "http://localhost:8002/api/v1/auth/login"
    
    # Use the test researcher account
    credentials = {
        "email": "researcher@test.com",
        "password": "Password123!"
    }
    
    print(f"🔐 Logging in as {credentials['email']}...")
    response = requests.post(login_url, json=credentials)
    
    if response.status_code == 200:
        data = response.json()
        token = data.get("access_token")
        print(f"✅ Login successful! Token: {token[:20]}...")
        return token
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(f"Response: {response.text}")
        return None


def test_wallet_balance(token):
    """Test wallet balance endpoint."""
    url = "http://localhost:8002/api/v1/wallet/balance"
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"\n📊 Testing GET {url}")
    response = requests.get(url, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("✅ SUCCESS: Wallet balance endpoint works!")
        return True
    elif response.status_code == 403:
        print("❌ FAILED: Still getting 403 Forbidden")
        return False
    else:
        print(f"⚠️  Unexpected status code: {response.status_code}")
        return False


def test_wallet_transactions(token):
    """Test wallet transactions endpoint."""
    url = "http://localhost:8002/api/v1/wallet/transactions?limit=5&offset=0"
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"\n📜 Testing GET {url}")
    response = requests.get(url, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("✅ SUCCESS: Wallet transactions endpoint works!")
        return True
    elif response.status_code == 403:
        print("❌ FAILED: Still getting 403 Forbidden")
        return False
    else:
        print(f"⚠️  Unexpected status code: {response.status_code}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("WALLET ENDPOINT 403 FIX VERIFICATION")
    print("=" * 60)
    
    # Get auth token
    token = get_auth_token()
    if not token:
        print("\n❌ Cannot proceed without auth token")
        sys.exit(1)
    
    # Test endpoints
    balance_ok = test_wallet_balance(token)
    transactions_ok = test_wallet_transactions(token)
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Wallet Balance: {'✅ PASS' if balance_ok else '❌ FAIL'}")
    print(f"Wallet Transactions: {'✅ PASS' if transactions_ok else '❌ FAIL'}")
    
    if balance_ok and transactions_ok:
        print("\n🎉 ALL TESTS PASSED! The 403 fix works!")
        sys.exit(0)
    else:
        print("\n❌ SOME TESTS FAILED")
        sys.exit(1)
