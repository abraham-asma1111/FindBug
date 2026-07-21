#!/usr/bin/env python3
"""
Test the researchers API endpoint with authentication
"""
import requests
import json

BASE_URL = "http://localhost:8002"

def test_endpoint():
    print("\n" + "="*60)
    print("  TESTING RESEARCHERS API WITH AUTHENTICATION")
    print("="*60 + "\n")
    
    # Step 1: Login as organization
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
        print(f"Response: {login_response.text}")
        
        # Try to create org user
        print("\n2. Trying to create organization user...")
        register_response = requests.post(
            f"{BASE_URL}/api/v1/auth/register",
            json={
                "email": "org@example.com",
                "password": "password123",
                "role": "organization"
            }
        )
        print(f"Register status: {register_response.status_code}")
        print(f"Response: {register_response.text[:200]}")
        return
    
    token = login_response.json().get("access_token")
    print(f"✅ Login successful")
    print(f"Token: {token[:30]}...\n")
    
    # Step 2: Test the researchers endpoint
    print("2. Testing GET /api/v1/matching/organization/researchers...")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/api/v1/matching/organization/researchers",
        headers=headers
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ SUCCESS! Got {len(data)} researchers\n")
        
        if data:
            print("First 3 researchers:")
            for researcher in data[:3]:
                print(f"\n- {researcher['user']['username']} ({researcher['user']['email']})")
                print(f"  Reputation: {researcher['reputation_score']}")
                print(f"  Reports: {researcher['total_reports']}")
        else:
            print("⚠️  No researchers returned (empty array)")
    else:
        print(f"❌ FAILED!")
        print(f"Response: {response.text}")
    
    # Step 3: Test with search
    print("\n3. Testing with search parameter...")
    response = requests.get(
        f"{BASE_URL}/api/v1/matching/organization/researchers?search=test",
        headers=headers
    )
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Got {len(data)} researchers matching 'test'")
    
    print("\n" + "="*60)
    print("  TEST COMPLETE")
    print("="*60 + "\n")

if __name__ == "__main__":
    try:
        test_endpoint()
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to backend at http://localhost:8002")
        print("Make sure the backend is running on port 8002!")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
