#!/usr/bin/env python3
"""
Test email verification with the token from the URL
"""
import requests
import json

def test_email_verification():
    """Test email verification with actual token"""
    print("🧪 Testing email verification...")
    
    base_url = "http://localhost:8002"
    
    # Use the token from your URL
    token = "verify-003bf66e-bf79-465a-a84e-e23b9d0e0886"
    
    try:
        # Test email verification
        print(f"\n🔗 Testing verification with token: {token}")
        response = requests.post(
            f"{base_url}/api/v1/registration/verify-email",
            json={"token": token},
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Verification successful: {data.get('message')}")
            print(f"Can login: {data.get('can_login')}")
            print(f"Email verified: {data.get('email_verified')}")
        else:
            print(f"❌ Verification failed: {response.text}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    test_email_verification()