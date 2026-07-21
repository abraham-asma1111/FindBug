#!/usr/bin/env python3
"""Test script to verify join program functionality."""

import requests
import json

API_URL = "http://127.0.0.1:8002/api/v1"

# Test credentials
ORG_EMAIL = "org@test.com"
ORG_PASSWORD = "Password123!"

RESEARCHER_EMAIL = "researcher@test.com"
RESEARCHER_PASSWORD = "Password123!"

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

def get_programs(token=None):
    """Get list of programs."""
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    response = requests.get(f"{API_URL}/programs", headers=headers)
    print(f"\n=== GET /programs ===")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        programs = response.json()
        print(f"Found {len(programs)} programs")
        for p in programs:
            print(f"  - {p['name']} (ID: {p['id']}, Status: {p['status']}, Visibility: {p.get('visibility', 'N/A')})")
        return programs
    else:
        print(f"Error: {response.text}")
        return []

def join_program(program_id, token):
    """Join a program."""
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"\n=== POST /programs/{program_id}/join ===")
    response = requests.post(
        f"{API_URL}/programs/{program_id}/join",
        headers=headers,
        json={}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    # Try to parse JSON response
    try:
        data = response.json()
        if isinstance(data, dict):
            for key, value in data.items():
                print(f"  {key}: {value}")
    except:
        pass
    
    return response.status_code == 200

def main():
    print("=" * 60)
    print("Testing Join Program Flow")
    print("=" * 60)
    
    # Login as organization
    print("\n1. Login as organization...")
    org_token = login(ORG_EMAIL, ORG_PASSWORD)
    if not org_token:
        print("Failed to login as organization")
        return
    print("✓ Organization logged in")
    
    # Login as researcher
    print("\n2. Login as researcher...")
    researcher_token = login(RESEARCHER_EMAIL, RESEARCHER_PASSWORD)
    if not researcher_token:
        print("Failed to login as researcher")
        return
    print("✓ Researcher logged in")
    
    # Get programs as researcher
    print("\n3. Get public programs as researcher...")
    programs = get_programs(researcher_token)
    
    if not programs:
        print("\n❌ No programs found. Please create and publish a program first.")
        return
    
    # Find a public program
    public_programs = [p for p in programs if p.get('status') == 'public']
    if not public_programs:
        print("\n❌ No public programs found. Please publish a program first.")
        print("\nAvailable programs:")
        for p in programs:
            print(f"  - {p['name']}: status={p['status']}, visibility={p.get('visibility')}")
        return
    
    # Try to join the first public program
    program = public_programs[0]
    print(f"\n4. Joining program: {program['name']} (ID: {program['id']})")
    success = join_program(program['id'], researcher_token)
    
    if success:
        print("\n✓ Successfully joined program!")
    else:
        print("\n❌ Failed to join program")

if __name__ == "__main__":
    main()
