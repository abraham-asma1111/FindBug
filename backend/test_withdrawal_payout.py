"""Test withdrawal creates payout request"""
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
    exit(1)

token = login_response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print("✅ Logged in successfully!")

# Get wallet balance
print("\n📊 Fetching wallet balance...")
balance_response = requests.get(f"{BASE_URL}/wallet/balance", headers=headers)
balance_data = balance_response.json()
print(f"Available Balance: {balance_data['available_balance']} ETB")

# Test withdrawal
print(f"\n💰 Submitting withdrawal request for 300 ETB...")
withdrawal_response = requests.post(
    f"{BASE_URL}/wallet/withdraw",
    headers=headers,
    json={
        "amount": 300,
        "payment_method": "bank_transfer",
        "account_details": {"bank": "CBE", "account": "1234567890"}
    }
)

print(f"\n📤 Withdrawal Response Status: {withdrawal_response.status_code}")
if withdrawal_response.status_code == 201:
    print("✅ Withdrawal request submitted!")
    print(json.dumps(withdrawal_response.json(), indent=2))
else:
    print(f"❌ Withdrawal failed:")
    print(withdrawal_response.text)
    exit(1)

# Now login as finance officer to see the payout
print("\n\n🔐 Logging in as finance officer...")
finance_login = requests.post(
    f"{BASE_URL}/auth/login",
    json={
        "email": "finance@findbug.com",
        "password": "Password123!"
    }
)

if finance_login.status_code != 200:
    print(f"❌ Finance login failed: {finance_login.status_code}")
    exit(1)

finance_token = finance_login.json()["access_token"]
finance_headers = {"Authorization": f"Bearer {finance_token}"}
print("✅ Logged in as finance officer!")

# Get pending payouts
print("\n📋 Fetching pending payouts...")
payouts_response = requests.get(f"{BASE_URL}/wallet/payouts?status=pending", headers=finance_headers)
print(f"Status: {payouts_response.status_code}")
if payouts_response.status_code == 200:
    payouts_data = payouts_response.json()
    print(f"✅ Found {payouts_data['total']} pending payout(s)")
    if payouts_data['total'] > 0:
        print(json.dumps(payouts_data['payouts'][0], indent=2))
else:
    print(f"❌ Failed to fetch payouts:")
    print(payouts_response.text)

print("\n✅ Test completed!")
