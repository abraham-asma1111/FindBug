#!/usr/bin/env python3
"""
Test script for researcher PTaaS endpoints
"""
import requests
import sys

BASE_URL = "http://localhost:8002/api/v1"

def test_researcher_endpoints():
    """Test researcher PTaaS endpoints"""
    
    print("=" * 60)
    print("Testing Researcher PTaaS Endpoints")
    print("=" * 60)
    
    # First, login as a researcher
    print("\n1. Logging in as researcher...")
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": "researcher@test.com",
            "password": "password123"
        }
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(f"Response: {login_response.text}")
        return False
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Login successful")
    
    # Test list researcher engagements
    print("\n2. Testing GET /ptaas/researcher/engagements...")
    response = requests.get(
        f"{BASE_URL}/ptaas/researcher/engagements",
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        engagements = response.json()
        print(f"✅ Found {len(engagements)} engagement(s)")
        for eng in engagements:
            print(f"   - {eng['name']} (Status: {eng['status']})")
    elif response.status_code == 404:
        print("❌ Endpoint not found - backend needs restart")
        print("   Run: cd backend && source venv/bin/activate && uvicorn src.main:app --reload --port 8002")
        return False
    else:
        print(f"❌ Request failed: {response.text}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ All tests passed!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = test_researcher_endpoints()
    sys.exit(0 if success else 1)
