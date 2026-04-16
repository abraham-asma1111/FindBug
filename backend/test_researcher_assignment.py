#!/usr/bin/env python3
"""
Test PTaaS Researcher Assignment
Tests the full flow: fetch researchers -> assign to engagement
"""
import requests
import json

BASE_URL = "http://localhost:8002/api/v1"

# You need to replace these with actual credentials
ORG_EMAIL = "org@example.com"  # Replace with your org user email
ORG_PASSWORD = "password123"    # Replace with your org user password

def login(email, password):
    """Login and get access token"""
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": email, "password": password}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Login failed: {response.status_code}")
        print(response.text)
        return None

def get_researchers(token):
    """Fetch available researchers"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/matching/organization/researchers?limit=100",
        headers=headers
    )
    print(f"\n=== GET RESEARCHERS ===")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        researchers = response.json()
        print(f"Found {len(researchers)} researchers")
        for r in researchers[:3]:  # Show first 3
            print(f"  - {r['user']['username']} ({r['user']['email']}) - Reputation: {r['reputation_score']}")
        return researchers
    else:
        print(f"Error: {response.text}")
        return []

def get_engagements(token):
    """Get PTaaS engagements"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/ptaas/engagements",
        headers=headers
    )
    print(f"\n=== GET ENGAGEMENTS ===")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        engagements = response.json()
        print(f"Found {len(engagements)} engagements")
        for e in engagements:
            print(f"  - {e['name']} (ID: {e['id']}) - Status: {e['status']}")
        return engagements
    else:
        print(f"Error: {response.text}")
        return []

def assign_researchers(token, engagement_id, researcher_ids):
    """Assign researchers to engagement"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{BASE_URL}/ptaas/engagements/{engagement_id}/assign",
        headers=headers,
        json={"researcher_ids": researcher_ids}
    )
    print(f"\n=== ASSIGN RESEARCHERS ===")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Success! Assigned {len(researcher_ids)} researchers")
        print(f"Engagement: {result['name']}")
        print(f"Team size: {result.get('team_size', 0)}")
        return result
    else:
        print(f"Error: {response.text}")
        return None

def main():
    print("=" * 60)
    print("PTaaS Researcher Assignment Test")
    print("=" * 60)
    
    # Step 1: Login
    print("\n[1] Logging in...")
    token = login(ORG_EMAIL, ORG_PASSWORD)
    if not token:
        print("❌ Login failed. Please check credentials.")
        return
    print("✅ Login successful")
    
    # Step 2: Get researchers
    print("\n[2] Fetching researchers...")
    researchers = get_researchers(token)
    if not researchers:
        print("❌ No researchers found or API error")
        return
    print(f"✅ Found {len(researchers)} researchers")
    
    # Step 3: Get engagements
    print("\n[3] Fetching engagements...")
    engagements = get_engagements(token)
    if not engagements:
        print("❌ No engagements found")
        return
    print(f"✅ Found {len(engagements)} engagements")
    
    # Step 4: Assign researchers to first engagement
    if len(researchers) > 0 and len(engagements) > 0:
        engagement_id = engagements[0]['id']
        # Assign first 2 researchers
        researcher_ids = [r['id'] for r in researchers[:2]]
        
        print(f"\n[4] Assigning {len(researcher_ids)} researchers to engagement {engagement_id}...")
        result = assign_researchers(token, engagement_id, researcher_ids)
        if result:
            print("✅ Assignment successful!")
        else:
            print("❌ Assignment failed")
    
    print("\n" + "=" * 60)
    print("Test complete!")
    print("=" * 60)

if __name__ == "__main__":
    print("\n⚠️  IMPORTANT: Update ORG_EMAIL and ORG_PASSWORD in this script first!\n")
    main()
