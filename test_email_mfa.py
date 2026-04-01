#!/usr/bin/env python3
"""
Test Email and MFA functionality
"""
import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8002/api/v1"
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "TestPass123!"

def test_email_verification():
    """Test email verification flow"""
    print("🧪 Testing Email Verification Flow")
    print("=" * 50)
    
    # 1. Register a new user
    print("1. Registering new researcher...")
    register_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "password_confirm": TEST_PASSWORD,
        "first_name": "Test",
        "last_name": "User"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register/researcher", json=register_data)
        if response.status_code == 201:
            print("✅ Registration successful")
            result = response.json()
            print(f"   User ID: {result.get('user_id')}")
            print(f"   Message: {result.get('message')}")
        else:
            print(f"❌ Registration failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return False
    
    # 2. Try to login (should fail - email not verified)
    print("\n2. Attempting login before email verification...")
    login_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 401:
            print("✅ Login correctly blocked - email not verified")
        else:
            print(f"⚠️  Unexpected login result: {response.status_code}")
    except Exception as e:
        print(f"❌ Login test error: {e}")
    
    # 3. Test resend verification
    print("\n3. Testing resend verification email...")
    resend_data = {"email": TEST_EMAIL}
    
    try:
        response = requests.post(f"{BASE_URL}/auth/resend-verification", json=resend_data)
        if response.status_code == 200:
            print("✅ Resend verification successful")
            print("   Check backend logs for email content")
        else:
            print(f"❌ Resend failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Resend error: {e}")
    
    return True

def test_mfa_flow():
    """Test MFA setup flow (requires verified user)"""
    print("\n🔐 Testing MFA Flow")
    print("=" * 50)
    
    # Note: This would require a verified user and valid JWT token
    # For now, we'll just test the endpoint availability
    
    print("1. Testing MFA endpoints availability...")
    
    endpoints = [
        "/auth/mfa/enable",
        "/auth/mfa/verify", 
        "/auth/mfa/disable"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.post(f"{BASE_URL}{endpoint}")
            if response.status_code == 401:
                print(f"✅ {endpoint} - Correctly requires authentication")
            else:
                print(f"⚠️  {endpoint} - Unexpected status: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint} - Error: {e}")
    
    return True

def test_email_templates():
    """Test email template seeding"""
    print("\n📧 Testing Email Templates")
    print("=" * 50)
    
    print("Running email template seeding script...")
    import subprocess
    import os
    
    try:
        # Change to backend directory and run seeding script
        backend_dir = "backend"
        if os.path.exists(backend_dir):
            result = subprocess.run(
                ["python", "scripts/seed_email_templates.py"],
                cwd=backend_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("✅ Email templates seeded successfully")
                print(result.stdout)
            else:
                print("❌ Email template seeding failed")
                print(result.stderr)
        else:
            print("⚠️  Backend directory not found, skipping template seeding")
    except Exception as e:
        print(f"❌ Template seeding error: {e}")

def main():
    """Main test function"""
    print("🚀 Starting Email and MFA Tests")
    print("=" * 60)
    
    # Check if backend is running
    try:
        response = requests.get(f"http://localhost:8002/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running")
        else:
            print("❌ Backend health check failed")
            return
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        print("   Make sure backend is running on port 8002")
        return
    
    # Run tests
    test_email_templates()
    test_email_verification()
    test_mfa_flow()
    
    print("\n" + "=" * 60)
    print("🎉 Email and MFA tests completed!")
    print("\nNext steps:")
    print("1. Configure SMTP settings in backend/.env")
    print("2. Test with real email provider")
    print("3. Test MFA setup with authenticated user")
    print("4. Verify email verification flow end-to-end")

if __name__ == "__main__":
    main()