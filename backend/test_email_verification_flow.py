#!/usr/bin/env python3
"""
Test script for email verification flow.
Tests the complete refactored email verification system.
"""

import requests
import json

BASE_URL = "http://localhost:8001/api/v1"

# Test user credentials
EMAIL = "abrahambecon@gmail.com"
PASSWORD = "Test123!@#"

def test_email_verification():
    """Test complete email verification flow."""
    
    print("=" * 60)
    print("EMAIL VERIFICATION FLOW TEST")
    print("=" * 60)
    
    # Step 1: Login
    print("\n1️⃣  Logging in...")
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": EMAIL, "password": PASSWORD}
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(login_response.text)
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"✅ Logged in successfully")
    
    # Step 2: Check email verification status
    print("\n2️⃣  Checking email verification status...")
    status_response = requests.get(
        f"{BASE_URL}/kyc/email/status",
        headers=headers
    )
    
    if status_response.status_code != 200:
        print(f"❌ Status check failed: {status_response.status_code}")
        print(status_response.text)
        return
    
    status_data = status_response.json()
    print(f"✅ Status retrieved:")
    print(f"   Email verified: {status_data.get('email_verified')}")
    print(f"   Email address: {status_data.get('email_address')}")
    print(f"   Can verify: {status_data.get('can_verify_email')}")
    
    # Step 3: Send verification code
    print("\n3️⃣  Sending verification code...")
    send_response = requests.post(
        f"{BASE_URL}/kyc/email/send",
        headers=headers,
        json={"email_address": EMAIL}
    )
    
    if send_response.status_code == 200:
        send_data = send_response.json()
        print(f"✅ Verification code sent!")
        print(f"   Email: {send_data.get('email_address')}")
        print(f"   Expires in: {send_data.get('expires_in_minutes')} minutes")
        print(f"\n📧 Check your email ({EMAIL}) for the 6-digit code")
        
        # Step 4: Prompt for code
        print("\n4️⃣  Enter the verification code from your email:")
        code = input("   Code: ").strip()
        
        if code:
            print(f"\n5️⃣  Verifying code...")
            verify_response = requests.post(
                f"{BASE_URL}/kyc/email/verify",
                headers=headers,
                json={"code": code}
            )
            
            if verify_response.status_code == 200:
                verify_data = verify_response.json()
                print(f"✅ Email verified successfully!")
                print(f"   Email: {verify_data.get('email_address')}")
                print(f"   Verified at: {verify_data.get('verified_at')}")
            else:
                print(f"❌ Verification failed: {verify_response.status_code}")
                print(verify_response.text)
        else:
            print("⏭️  Skipping verification (no code entered)")
    
    elif send_response.status_code == 409:
        print(f"ℹ️  Email already verified")
    else:
        print(f"❌ Send failed: {send_response.status_code}")
        print(send_response.text)
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_email_verification()
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend server")
        print("   Make sure the server is running on http://localhost:8001")
    except Exception as e:
        print(f"❌ Error: {e}")
