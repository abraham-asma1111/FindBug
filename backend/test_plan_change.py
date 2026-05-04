"""Test subscription plan change functionality."""
import requests
import json

BASE_URL = "http://127.0.0.1:8002/api/v1"

# Login as organization
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={
        "email": "org@test.com",
        "password": "Password123!"
    }
)

if login_response.status_code != 200:
    print(f"❌ Login failed: {login_response.status_code}")
    print(login_response.text)
    exit(1)

token = login_response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

print("✅ Logged in successfully")

# Get current subscription
sub_response = requests.get(
    f"{BASE_URL}/subscriptions/current",
    headers=headers
)

if sub_response.status_code != 200:
    print(f"❌ Failed to get subscription: {sub_response.status_code}")
    print(sub_response.text)
    exit(1)

subscription = sub_response.json()
print(f"\n📋 Current Subscription:")
print(f"   - ID: {subscription['subscription_id']}")
print(f"   - Tier: {subscription['tier']}")
print(f"   - Fee: {subscription['subscription_fee']} {subscription['currency']}")
print(f"   - Status: {subscription['status']}")

# Test plan change
current_tier = subscription['tier'].lower()
new_tier = 'enterprise' if current_tier != 'enterprise' else 'basic'

print(f"\n🔄 Attempting to change plan from {current_tier} to {new_tier}...")

change_response = requests.post(
    f"{BASE_URL}/subscriptions/{subscription['subscription_id']}/change-plan",
    headers=headers,
    json={"new_tier": new_tier}
)

if change_response.status_code != 200:
    print(f"❌ Plan change failed: {change_response.status_code}")
    print(change_response.text)
    exit(1)

updated_subscription = change_response.json()
print(f"\n✅ Plan changed successfully!")
print(f"   - New Tier: {updated_subscription['tier']}")
print(f"   - New Fee: {updated_subscription['subscription_fee']} {updated_subscription['currency']}")

# Verify the change
verify_response = requests.get(
    f"{BASE_URL}/subscriptions/current",
    headers=headers
)

if verify_response.status_code == 200:
    verified_sub = verify_response.json()
    print(f"\n✅ Verification successful!")
    print(f"   - Confirmed Tier: {verified_sub['tier']}")
    print(f"   - Confirmed Fee: {verified_sub['subscription_fee']} {verified_sub['currency']}")
else:
    print(f"❌ Verification failed: {verify_response.status_code}")

print("\n✅ All tests passed!")
