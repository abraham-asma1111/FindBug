#!/usr/bin/env python3
"""
Test organization user profile endpoint
"""
import requests
import sys

BASE_URL = "http://localhost:8000"

def test_org_profile():
    """Test organization user profile"""
    
    # Login as organization
    print("1. Logging in as organization...")
    login_response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={
            "email": "org@example.com",
            "password": "password123"
        }
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(login_response.text)
        return False
    
    login_data = login_response.json()
    token = login_data.get("access_token")
    print(f"✅ Login successful")
    print(f"   Role: {login_data.get('role')}")
    print(f"   User ID: {login_data.get('user_id')}")
    
    # Get profile
    print("\n2. Fetching /users/me profile...")
    headers = {"Authorization": f"Bearer {token}"}
    profile_response = requests.get(
        f"{BASE_URL}/api/v1/users/me",
        headers=headers
    )
    
    if profile_response.status_code != 200:
        print(f"❌ Profile fetch failed: {profile_response.status_code}")
        print(profile_response.text)
        return False
    
    profile_data = profile_response.json()
    print(f"✅ Profile fetched successfully")
    print(f"\nProfile data:")
    print(f"   ID: {profile_data.get('id')}")
    print(f"   Email: {profile_data.get('email')}")
    print(f"   Role: {profile_data.get('role')}")
    print(f"   Organization: {profile_data.get('organization')}")
    
    if not profile_data.get('organization'):
        print("\n⚠️  WARNING: 'organization' field is missing or null!")
        print("   This is why the organization portal pages show empty data.")
        return False
    
    print("\n✅ Organization data is present:")
    org_data = profile_data.get('organization', {})
    print(f"   Company Name: {org_data.get('company_name')}")
    print(f"   Industry: {org_data.get('industry')}")
    print(f"   Website: {org_data.get('website')}")
    
    return True

if __name__ == "__main__":
    success = test_org_profile()
    sys.exit(0 if success else 1)
