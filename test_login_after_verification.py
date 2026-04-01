#!/usr/bin/env python3
"""
Test login after email verification
"""
import requests

def test_login_after_verification():
    """Test that user can login after email verification"""
    print("🧪 Testing login after verification...")
    
    base_url = "http://localhost:8002"
    
    # Test data (same as registration)
    test_data = {
        "email": "testuser@example.com",
        "password": "TestPass123!"
    }
    
    try:
        # Try to login
        print("\n🔐 Testing login after verification...")
        login_response = requests.post(
            f"{base_url}/api/v1/auth/login",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Login status: {login_response.status_code}")
        print(f"Login response: {login_response.text}")
        
        if login_response.status_code == 200:
            data = login_response.json()
            print("✅ Login successful after verification!")
            print(f"User: {data.get('user', {}).get('email')}")
            print(f"Role: {data.get('user', {}).get('role')}")
            return True
        else:
            print(f"❌ Login failed: {login_response.text}")
            return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    test_login_after_verification()