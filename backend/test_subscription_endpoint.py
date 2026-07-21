"""Test subscription endpoint with organization user."""
import requests
import json

# Backend URL
BASE_URL = "http://127.0.0.1:8002/api/v1"

# Organization credentials
ORG_EMAIL = "org@test.com"
ORG_PASSWORD = "Password123!"

def test_subscription_endpoint():
    """Test the subscription endpoint."""
    
    # Step 1: Login as organization
    print("Step 1: Logging in as organization...")
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": ORG_EMAIL,
            "password": ORG_PASSWORD
        }
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(f"Response: {login_response.text}")
        return
    
    login_data = login_response.json()
    access_token = login_data.get("access_token")
    print(f"✅ Login successful! Token: {access_token[:20]}...")
    
    # Step 2: Get user profile
    print("\nStep 2: Getting user profile...")
    headers = {"Authorization": f"Bearer {access_token}"}
    profile_response = requests.get(f"{BASE_URL}/users/me", headers=headers)
    
    if profile_response.status_code != 200:
        print(f"❌ Profile fetch failed: {profile_response.status_code}")
        print(f"Response: {profile_response.text}")
        return
    
    profile_data = profile_response.json()
    print(f"✅ Profile fetched!")
    print(f"   User ID: {profile_data.get('id')}")
    print(f"   Email: {profile_data.get('email')}")
    print(f"   Role: {profile_data.get('role')}")
    
    # Step 3: Get current subscription
    print("\nStep 3: Getting current subscription...")
    subscription_response = requests.get(
        f"{BASE_URL}/subscriptions/current",
        headers=headers
    )
    
    print(f"Status Code: {subscription_response.status_code}")
    print(f"Response: {json.dumps(subscription_response.json(), indent=2)}")
    
    if subscription_response.status_code == 200:
        print("✅ Subscription fetched successfully!")
    elif subscription_response.status_code == 404:
        print("⚠️  No active subscription found (404)")
    elif subscription_response.status_code == 403:
        print("❌ Access forbidden (403) - Authorization issue")
    else:
        print(f"❌ Unexpected status code: {subscription_response.status_code}")

if __name__ == "__main__":
    test_subscription_endpoint()
