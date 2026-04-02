#!/usr/bin/env python3
"""Debug join program issue."""

import sys
import os
import requests

sys.path.insert(0, os.path.dirname(__file__))

API_URL = "http://127.0.0.1:8002/api/v1"

def login(email, password):
    """Login and get access token."""
    response = requests.post(
        f"{API_URL}/auth/login",
        json={"email": email, "password": password}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Login failed: {response.status_code} - {response.text}")
        return None

def join_program(program_id, token):
    """Join a program and print full response."""
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"\n=== Attempting to join program {program_id} ===")
    try:
        response = requests.post(
            f"{API_URL}/programs/{program_id}/join",
            headers=headers,
            json={},
            timeout=10
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 500:
            print("\n❌ 500 Internal Server Error - Check backend logs for details")
            print("The error is happening on the server side.")
        
        return response
    except Exception as e:
        print(f"Request failed with exception: {e}")
        return None

def main():
    # Login as researcher
    print("Logging in as researcher...")
    token = login("researcher@test.com", "Password123!")
    
    if not token:
        print("Failed to login")
        return
    
    print("✓ Logged in successfully")
    
    # Try to join a program
    program_id = "ade9b88b-d3e2-444b-9546-fdf9eac0a273"
    response = join_program(program_id, token)
    
    if response and response.status_code == 200:
        print("\n✓ Successfully joined program!")
    else:
        print("\n❌ Failed to join program")
        print("\nTo debug further, check the backend terminal for the actual Python error.")

if __name__ == "__main__":
    main()
