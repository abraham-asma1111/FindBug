#!/usr/bin/env python3
"""
Test Simple Registration Flow - HackerOne Style
"""
import requests
import json

BASE_URL = "http://localhost:8002/api/v1"

def test_simple_registration():
    """Test the simple registration flow"""
    print("🚀 Testing Simple Registration (HackerOne Style)")
    print("=" * 60)
    
    # Test data
    test_email = input("Enter your email to test: ").strip()
    if not test_email:
        print("❌ No email provided")
        return
    
    test_data = {
        "email": test_email,
        "password": "TestPass123!",
        "first_name": "Test",
        "last_name": "User"
    }
    
    print(f"📧 Testing with: {test_email}")
    
    # Test registration
    try:
        print("\n1. 🎯 Creating Account...")
        response = requests.post(f"{BASE_URL}/auth/register/researcher", json=test_data)
        
        if response.status_code == 201:
            result = response.json()
            print("✅ Account created successfully!")
            print(f"   User ID: {result.get('user_id')}")
            print(f"   Email: {result.get('email')}")
            print(f"   Can Login: {result.get('can_login')}")
            print(f"   Email Verified: {result.get('email_verified')}")
            print(f"   Message: {result.get('message')}")
            
            # Test login immediately
            print("\n2. 🔑 Testing Login...")
            login_data = {
                "email": test_email,
                "password": "TestPass123!"
            }
            
            login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
            
            if login_response.status_code == 200:
                login_result = login_response.json()
                print("✅ Login successful!")
                print(f"   Access Token: {login_result.get('access_token')[:20]}...")
                print(f"   User Role: {login_result.get('user', {}).get('role')}")
                print(f"   Email Verified: {login_result.get('user', {}).get('is_verified')}")
            else:
                print(f"❌ Login failed: {login_response.text}")
            
        else:
            print(f"❌ Registration failed: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend. Is it running on port 8002?")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_email_service():
    """Test email service directly"""
    print("\n🧪 Testing Email Service")
    print("=" * 40)
    
    try:
        import sys
        import os
        sys.path.append('backend/src')
        
        from core.email_service import EmailService
        
        test_email = input("Enter your email to test email service: ").strip()
        if not test_email:
            print("❌ No email provided")
            return
        
        # Test sending verification email
        success = EmailService.send_email_verification_link(
            email=test_email,
            token="test-token-123",
            user_type="researcher"
        )
        
        if success:
            print("✅ Email sent successfully!")
            print(f"   Check your inbox: {test_email}")
        else:
            print("❌ Failed to send email")
            print("   Check Gmail credentials in backend/.env")
            
    except Exception as e:
        print(f"❌ Email service error: {e}")

if __name__ == "__main__":
    print("🎯 Simple Registration Test Suite")
    print("=" * 70)
    
    choice = input("Choose test:\n1. Registration Flow\n2. Email Service Only\nEnter choice (1 or 2): ").strip()
    
    if choice == "1":
        test_simple_registration()
    elif choice == "2":
        test_email_service()
    else:
        print("Invalid choice")