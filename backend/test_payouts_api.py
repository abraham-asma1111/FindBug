"""Test payouts API endpoint"""
import requests
import json

# Backend URL
BASE_URL = "http://127.0.0.1:8002/api/v1"

# Login as finance officer
print("🔐 Logging in as finance officer...")
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={
        "email": "finance@findbug.com",
        "password": "Finance123!"
    }
)

if login_response.status_code != 200:
    print(f"❌ Finance login failed: {login_response.status_code}")
    print(login_response.text)
    exit(1)

token = login_response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print("✅ Logged in as finance officer!")

# Get pending payouts
print("\n📋 Fetching pending payouts...")
payouts_response = requests.get(f"{BASE_URL}/wallet/payouts?status=pending", headers=headers)
print(f"Status: {payouts_response.status_code}")

if payouts_response.status_code == 200:
    payouts_data = payouts_response.json()
    print(f"✅ Found {payouts_data['total']} pending payout(s)")
    if payouts_data['total'] > 0:
        print("\nFirst payout:")
        print(json.dumps(payouts_data['payouts'][0], indent=2))
else:
    print(f"❌ Failed to fetch payouts:")
    print(payouts_response.text)

print("\n✅ Test completed!")
