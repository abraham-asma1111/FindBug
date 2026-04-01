#!/usr/bin/env python3
"""
Test the pending registration flow
"""
import requests
import json

def test_pending_registration():
    """Test the new pending registration flow"""
    print("🧪 Testing pending registration flow...")
    
    base_url = "http://localhost:8002"
    
    # Test data
    test_data = {
        "email": "testuser@example.com",
        "password": "TestPass123!",
        "first_name": "Test",
        "last_name": "User"
    }
    
    try:
        # 1. Test researcher registration
        print("\n1️⃣ Testing researcher registration...")
        response = requests.post(
            f"{base_url}/api/v1/registration/researcher/initiate",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Registration initiated: {data.get('message')}")
            print(f"Can login: {data.get('can_login')}")
            print(f"Email verified: {data.get('email_verified')}")
        else:
            print(f"❌ Registration failed: {response.text}")
            return False
        
        # 2. Try to login (should fail - not verified)
        print("\n2️⃣ Testing login before verification...")
        login_response = requests.post(
            f"{base_url}/api/v1/auth/login",
            json={
                "email": test_data["email"],
                "password": test_data["password"]
            },
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Login status: {login_response.status_code}")
        print(f"Login response: {login_response.text}")
        
        if login_response.status_code == 401:
            print("✅ Login correctly blocked before verification")
        else:
            print("⚠️ Login should be blocked before verification")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    test_pending_registration()