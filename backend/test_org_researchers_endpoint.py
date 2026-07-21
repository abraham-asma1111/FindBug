#!/usr/bin/env python3
"""
Test the organization/researchers endpoint directly
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import requests
import json

# Test configuration
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api/v1/matching/organization/researchers"

def test_endpoint():
    print("\n" + "="*60)
    print("  TESTING ORGANIZATION RESEARCHERS ENDPOINT")
    print("="*60 + "\n")
    
    # First, login as organization to get token
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
        return
    
    token = login_response.json().get("access_token")
    print(f"✅ Login successful, got token: {token[:20]}...")
    
    # Test the endpoint
    print("\n2. Testing GET /api/v1/matching/organization/researchers...")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(API_URL, headers=headers)
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ SUCCESS! Got {len(data)} researchers")
        
        if data:
            print("\nFirst researcher:")
            print(json.dumps(data[0], indent=2))
        else:
            print("\n⚠️  No researchers returned (empty array)")
    else:
        print(f"\n❌ FAILED!")
        print(f"Response: {response.text}")
    
    # Test with search parameter
    print("\n3. Testing with search parameter...")
    response = requests.get(
        f"{API_URL}?search=test",
        headers=headers
    )
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Got {len(data)} researchers matching 'test'")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    try:
        test_endpoint()
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to backend at http://localhost:8000")
        print("Make sure the backend is running!")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
