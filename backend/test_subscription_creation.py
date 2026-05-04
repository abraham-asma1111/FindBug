"""Test subscription creation flow"""
import requests
import json

BASE_URL = "http://127.0.0.1:8002/api/v1"

# Login as organization
print("🔐 Logging in as org@test.com...")
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
print(f"✅ Login successful")

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Get user info (user ID is the organization ID)
print("\n📋 Getting user info...")
user_response = requests.get(
    f"{BASE_URL}/users/me",
    headers=headers
)

if user_response.status_code != 200:
    print(f"❌ Failed to get user: {user_response.status_code}")
    print(user_response.text)
    exit(1)

user_data = user_response.json()
org_id = user_data["id"]  # User ID is the organization ID
print(f"✅ User/Organization ID: {org_id}")

# Check current subscription (should be 404)
print("\n🔍 Checking current subscription...")
sub_response = requests.get(
    f"{BASE_URL}/subscriptions/current",
    headers=headers
)

if sub_response.status_code == 404:
    print("✅ No subscription found (expected)")
elif sub_response.status_code == 200:
    print("⚠️  Subscription already exists:")
    print(json.dumps(sub_response.json(), indent=2))
else:
    print(f"❌ Unexpected response: {sub_response.status_code}")
    print(sub_response.text)

# Create subscription for Basic tier
print("\n💳 Creating Basic tier subscription...")
create_response = requests.post(
    f"{BASE_URL}/subscriptions",
    headers=headers,
    json={
        "organization_id": org_id,
        "tier": "basic",
        "trial_days": 0
    }
)

if create_response.status_code == 201:
    print("✅ Subscription created successfully!")
    subscription = create_response.json()
    print(f"   - Subscription ID: {subscription['subscription_id']}")
    print(f"   - Tier: {subscription['tier']}")
    print(f"   - Status: {subscription['status']}")
    print(f"   - Fee: {subscription['subscription_fee']} {subscription['currency']}")
elif create_response.status_code == 400:
    print(f"⚠️  Subscription creation failed (may already exist):")
    print(create_response.json())
else:
    print(f"❌ Subscription creation failed: {create_response.status_code}")
    print(create_response.text)
    exit(1)

# Verify subscription was created
print("\n🔍 Verifying subscription...")
verify_response = requests.get(
    f"{BASE_URL}/subscriptions/current",
    headers=headers
)

if verify_response.status_code == 200:
    print("✅ Subscription verified!")
    subscription = verify_response.json()
    print(f"   - Tier: {subscription['tier']}")
    print(f"   - Status: {subscription['status']}")
    print(f"   - Fee: {subscription['subscription_fee']} {subscription['currency']}")
else:
    print(f"❌ Failed to verify subscription: {verify_response.status_code}")
    print(verify_response.text)

print("\n✅ Test complete!")
