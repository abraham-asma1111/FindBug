"""
Test Persona KYC API endpoint directly
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import requests

def test_persona_status():
    """Test the Persona status endpoint"""
    
    # Login first to get token
    login_response = requests.post(
        "http://localhost:8002/api/v1/auth/login",
        json={
            "email": "researcher@example.com",
            "password": "password123"
        }
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(login_response.text)
        return
    
    token = login_response.json()["access_token"]
    print(f"✅ Login successful")
    
    # Test Persona status endpoint
    status_response = requests.get(
        "http://localhost:8002/api/v1/kyc/persona/status",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    print(f"\n📋 Persona Status Endpoint Response:")
    print(f"   Status Code: {status_response.status_code}")
    print(f"   Response: {status_response.json()}")

if __name__ == "__main__":
    test_persona_status()
