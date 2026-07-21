#!/usr/bin/env python3
"""
Test triage specialist login
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import requests

def test_login():
    print("\n" + "="*60)
    print("  TESTING TRIAGE SPECIALIST LOGIN")
    print("="*60 + "\n")
    
    url = "http://localhost:8000/api/v1/auth/login"
    payload = {
        "email": "triage@example.com",
        "password": "password123"
    }
    
    print(f"POST {url}")
    print(f"Payload: {payload}\n")
    
    try:
        response = requests.post(url, json=payload)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}\n")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ LOGIN SUCCESSFUL!")
            print(f"   Access Token: {data.get('access_token', 'N/A')[:50]}...")
            print(f"   User Role: {data.get('user', {}).get('role', 'N/A')}")
            print(f"   User Email: {data.get('user', {}).get('email', 'N/A')}")
        else:
            print("❌ LOGIN FAILED!")
            print(f"   Error: {response.json().get('detail', 'Unknown error')}")
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to backend server")
        print("   Make sure the backend is running:")
        print("   cd backend && uvicorn src.main:app --reload")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    test_login()
