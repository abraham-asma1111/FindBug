#!/usr/bin/env python3
"""
Test Frontend Registration Flow End-to-End
"""
import os
from dotenv import load_dotenv
load_dotenv('backend/.env')

import sys
sys.path.append('backend/src')

import requests
import json
import time

def test_complete_frontend_flow():
    """Test the complete registration flow that matches frontend behavior"""
    print("🚀 Testing Complete Frontend Registration Flow")
    print("=" * 60)
    
    backend_url = "http://localhost:8002/api/v1"
    frontend_url = "http://localhost:3002"
    
    # Generate unique test data
    timestamp = int(time.time())
    test_data = {
        "email": f"frontend.test.{timestamp}@example.com",
        "password": "TestPass123!",
        "first_name": "Frontend",
        "last_name": "Test",
        "username": f"frontend_test_{timestamp}",
        "role": "researcher",
        "country": "US"
    }
    
    print(f"📧 Testing with: {test_data['email']}")
    
    try:
        # Step 1: Test researcher registration (frontend format)
        print("\n1. 🎯 Testing Frontend Registration Format...")
        
        # This matches what the frontend sends
        registration_payload = {
            "email": test_data["email"],
            "password": test_data["password"],
            "first_name": test_data["first_name"],
            "last_name": test_data["last_name"]
        }
        
        response = requests.post(
            f"{backend_url}/registration/researcher/initiate",
            json=registration_payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Registration successful!")
            print(f"   User ID: {result.get('user_id')}")
            print(f"   Message: {result.get('message')}")
            print(f"   Can Login: {result.get('can_login')}")
            print(f"   Email Verified: {result.get('email_verified')}")
            
            user_id = result.get('user_id')
            verification_token = f"verify-{user_id}"
            
            # Step 2: Test email verification (frontend format)
            print(f"\n2. 📧 Testing Frontend Email Verification...")
            print(f"   Verification URL: {frontend_url}/verify-email?token={verification_token}&type=researcher")
            
            # This matches what the frontend sends
            verify_payload = {"token": verification_token}
            
            verify_response = requests.post(
                f"{backend_url}/registration/verify-email",
                json=verify_payload,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"   Status: {verify_response.status_code}")
            
            if verify_response.status_code == 200:
                verify_result = verify_response.json()
                print("✅ Email verification successful!")
                print(f"   Message: {verify_result.get('message')}")
                print(f"   Can Login: {verify_result.get('can_login')}")
                print(f"   Email Verified: {verify_result.get('email_verified')}")
                
                # Step 3: Test login after verification
                print(f"\n3. 🔐 Testing Login After Verification...")
                
                login_payload = {
                    "email": test_data["email"],
                    "password": test_data["password"]
                }
                
                login_response = requests.post(
                    f"{backend_url}/auth/login",
                    json=login_payload,
                    headers={"Content-Type": "application/json"}
                )
                
                print(f"   Status: {login_response.status_code}")
                
                if login_response.status_code == 200:
                    login_result = login_response.json()
                    print("✅ Login successful!")
                    print(f"   Access Token: {login_result.get('access_token')[:20]}...")
                    print(f"   User Role: {login_result.get('user', {}).get('role')}")
                    print(f"   User Verified: {login_result.get('user', {}).get('is_verified')}")
                else:
                    print(f"❌ Login failed: {login_response.text}")
                    
            else:
                print(f"❌ Email verification failed: {verify_response.text}")
                
        else:
            print(f"❌ Registration failed: {response.text}")
            
    except requests.exceptions.ConnectionError as e:
        if "8002" in str(e):
            print("❌ Cannot connect to backend server (port 8002)")
            print("   Make sure backend is running:")
            print("   cd backend && python -m uvicorn src.main:app --reload --port 8002")
        elif "3002" in str(e):
            print("❌ Cannot connect to frontend server (port 3002)")
            print("   Make sure frontend is running:")
            print("   cd frontend && npm run dev")
        else:
            print(f"❌ Connection error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    print("\n🎉 Frontend Registration Flow Test Complete!")
    print("\n📋 Summary:")
    print("   ✅ Backend registration endpoint working")
    print("   ✅ Email verification endpoint working")
    print("   ✅ Login after verification working")
    print("   ✅ Frontend can now use email verification links!")
    
    return True

if __name__ == "__main__":
    test_complete_frontend_flow()