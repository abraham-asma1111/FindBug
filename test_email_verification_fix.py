#!/usr/bin/env python3
"""
Test Email Verification Fix
"""
import os
from dotenv import load_dotenv
load_dotenv('backend/.env')

import sys
sys.path.append('backend/src')

import requests
import json

def test_registration_and_verification():
    """Test the complete registration and email verification flow"""
    print("🚀 Testing Registration and Email Verification Flow")
    print("=" * 60)
    
    base_url = "http://localhost:8002/api/v1"
    
    # Test data - use timestamp to make email unique
    import time
    timestamp = int(time.time())
    test_data = {
        "email": f"test.researcher.{timestamp}@example.com",
        "password": "TestPass123!",
        "first_name": "Test",
        "last_name": "Researcher"
    }
    
    print(f"📧 Testing with: {test_data['email']}")
    
    try:
        # Step 1: Register researcher
        print("\n1. 🎯 Testing Researcher Registration...")
        response = requests.post(
            f"{base_url}/registration/researcher/initiate",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Registration successful!")
            print(f"   User ID: {result.get('user_id')}")
            print(f"   Message: {result.get('message')}")
            print(f"   Can Login: {result.get('can_login')}")
            print(f"   Email Verified: {result.get('email_verified')}")
            
            # Extract user ID for verification token
            user_id = result.get('user_id')
            verification_token = f"verify-{user_id}"
            
            # Step 2: Test email verification
            print(f"\n2. 📧 Testing Email Verification...")
            print(f"   Token: {verification_token}")
            
            verify_response = requests.post(
                f"{base_url}/registration/verify-email",
                json={"token": verification_token},
                headers={"Content-Type": "application/json"}
            )
            
            if verify_response.status_code == 200:
                verify_result = verify_response.json()
                print("✅ Email verification successful!")
                print(f"   Message: {verify_result.get('message')}")
                print(f"   Can Login: {verify_result.get('can_login')}")
                print(f"   Email Verified: {verify_result.get('email_verified')}")
            else:
                print(f"❌ Email verification failed: {verify_response.status_code}")
                print(f"   Error: {verify_response.text}")
                
        else:
            print(f"❌ Registration failed: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend server")
        print("   Make sure backend is running on port 8002")
        print("   Run: cd backend && python -m uvicorn src.main:app --reload --port 8002")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    print("\n🎉 Email Verification Test Complete!")
    return True

if __name__ == "__main__":
    test_registration_and_verification()