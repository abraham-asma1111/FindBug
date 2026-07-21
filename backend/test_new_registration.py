#!/usr/bin/env python3
"""
Test new user registration flow
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import requests

def test_registration():
    """Test researcher registration"""
    
    base_url = "http://localhost:8001/api/v1"
    
    # Test data
    email = "lemec77126@ryzid.com"
    password = "TestPassword123!"
    first_name = "Test"
    last_name = "User"
    
    print(f"\n{'='*60}")
    print(f"TESTING REGISTRATION FOR: {email}")
    print(f"{'='*60}\n")
    
    # Step 1: Initiate registration
    print("📝 Step 1: Initiating registration...")
    try:
        response = requests.post(
            f"{base_url}/registration/researcher/initiate",
            json={
                "email": email,
                "password": password,
                "first_name": first_name,
                "last_name": last_name
            }
        )
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        if response.status_code == 200:
            print("   ✅ Registration initiated successfully!")
            print("   📧 Check email for verification link")
        else:
            print(f"   ❌ Registration failed: {response.json()}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False
    
    print(f"\n{'='*60}")
    print("✅ Registration test complete!")
    print(f"{'='*60}\n")
    
    print("📋 NEXT STEPS:")
    print("   1. Check email: lemec77126@ryzid.com")
    print("   2. Click verification link")
    print("   3. Login with credentials")
    print("   4. Complete KYC verification")
    
    return True

if __name__ == "__main__":
    test_registration()
