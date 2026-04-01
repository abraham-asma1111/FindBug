#!/usr/bin/env python3
"""
Test script for authentication flow
Tests registration and login endpoints
"""

import requests
import json
import sys
import time

BASE_URL = "http://localhost:8002"

def test_registration():
    """Test user registration"""
    print("🧪 Testing User Registration...")
    
    # Use timestamp to make email unique
    timestamp = int(time.time())
    email = f"test{timestamp}@example.com"
    
    # Test data for researcher registration
    registration_data = {
        "email": email,
        "password": "TestPassword123!",
        "password_confirm": "TestPassword123!",
        "first_name": "Test",
        "last_name": "User"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/register/researcher",
            json=registration_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 201:
            print("✅ Registration successful!")
            result = response.json()
            result['test_email'] = email  # Add email to result for login test
            return result
        else:
            print("❌ Registration failed!")
            return None
            
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return None

def test_login(email):
    """Test user login"""
    print("\n🧪 Testing User Login...")
    
    # Login data (JSON format as expected by the backend)
    login_data = {
        "email": email,
        "password": "TestPassword123!"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            json=login_data,  # JSON data, not form data
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Login successful!")
            return response.json()
        else:
            print("❌ Login failed!")
            return None
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_protected_endpoint(access_token):
    """Test accessing a protected endpoint"""
    print("\n🧪 Testing Protected Endpoint...")
    
    try:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{BASE_URL}/api/v1/users/me",
            headers=headers
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Protected endpoint access successful!")
            return response.json()
        else:
            print("❌ Protected endpoint access failed!")
            return None
            
    except Exception as e:
        print(f"❌ Protected endpoint error: {e}")
        return None

def main():
    print("🚀 Starting Authentication Flow Test")
    print("=" * 50)
    
    # Test registration
    registration_result = test_registration()
    
    if not registration_result:
        print("❌ Registration failed, stopping tests")
        sys.exit(1)
    
    print(f"✅ Registration successful! User ID: {registration_result.get('user_id')}")
    print(f"📧 Email verification required for: {registration_result.get('email')}")
    
    # Test login (will fail until email is verified, but let's test the endpoint)
    test_email = registration_result.get('test_email')
    login_result = test_login(test_email)
    
    if login_result:
        access_token = login_result.get("access_token")
        if access_token:
            # Test protected endpoint
            user_info = test_protected_endpoint(access_token)
            if user_info:
                print(f"\n✅ User Info: {json.dumps(user_info, indent=2)}")
    else:
        print("ℹ️  Login failed (expected - email verification required)")
    
    print("\n🎉 Authentication flow test completed!")
    print("📝 Next steps:")
    print("   1. Check email for verification link")
    print("   2. Click verification link")
    print("   3. Try login again")

if __name__ == "__main__":
    main()