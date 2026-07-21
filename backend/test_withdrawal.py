"""Test withdrawal functionality"""
import requests
import json

# Backend URL
BASE_URL = "http://127.0.0.1:8002/api/v1"

# Login as researcher
print("🔐 Logging in as researcher@test.com...")
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={
        "email": "researcher@test.com",
        "password": "Password123!"
    }
)

if login_response.status_code != 200:
    print(f"❌ Login failed: {login_response.status_code}")
    print(login_response.text)
    exit(1)

token = login_response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

print("✅ Logged in successfully!")

# Get wallet balance
print("\n📊 Fetching wallet balance...")
balance_response = requests.get(f"{BASE_URL}/wallet/balance", headers=headers)
print(json.dumps(balance_response.json(), indent=2))

balance_data = balance_response.json()
available = balance_data.get("available_balance", 0)

if available < 100:
    print(f"\n⚠️  Insufficient balance for withdrawal (need at least 100 ETB, have {available} ETB)")
    exit(0)

# Test withdrawal
print(f"\n💰 Testing withdrawal of 500 ETB...")
withdrawal_response = requests.post(
    f"{BASE_URL}/wallet/withdraw",
    headers=headers,
    json={
        "amount": 500,
        "payment_method": "bank_transfer",
        "account_details": {}
    }
)

print(f"\n📤 Withdrawal Response Status: {withdrawal_response.status_code}")
if withdrawal_response.status_code == 201:
    print("✅ Withdrawal request submitted successfully!")
    print(json.dumps(withdrawal_response.json(), indent=2))
else:
    print(f"❌ Withdrawal failed:")
    print(json.dumps(withdrawal_response.json(), indent=2))

# Get updated balance
print(f"\n📊 Fetching updated wallet balance...")
balance_response = requests.get(f"{BASE_URL}/wallet/balance", headers=headers)
print(json.dumps(balance_response.json(), indent=2))

print("\n✅ Test completed!")
