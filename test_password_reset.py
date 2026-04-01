#!/usr/bin/env python3
"""
Test password reset flow
"""
import requests

def test_password_reset():
    """Test the password reset flow"""
    print("🧪 Testing password reset flow...")
    
    base_url = "http://localhost:8002"
    
    # Use an existing user email
    email = "testuser@example.com"
    
    try:
        # 1. Request password reset
        print("\n1️⃣ Requesting password reset...")
        response = requests.post(
            f"{base_url}/api/v1/auth/forgot-password",
            json={"email": email},
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Password reset email sent!")
            print("📧 Check your email for the reset link")
        else:
            print(f"❌ Failed: {response.text}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    test_password_reset()