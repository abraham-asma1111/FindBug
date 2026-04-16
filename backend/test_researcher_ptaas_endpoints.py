#!/usr/bin/env python3
"""
Test script for researcher PTaaS endpoints
"""
import requests
import json

BASE_URL = "http://localhost:8002/api/v1"

def test_researcher_endpoints():
    """Test researcher PTaaS endpoints"""
    
    print("=" * 60)
    print("Testing Researcher PTaaS Endpoints")
    print("=" * 60)
    
    # First, login as a researcher
    print("\n1. Logging in as researcher...")
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": "researcher@test.com",
            "password": "Password123!"
        }
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(login_response.text)
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Login successful")
    
    # Test: List researcher engagements
    print("\n2. Fetching researcher engagements...")
    engagements_response = requests.get(
        f"{BASE_URL}/ptaas/researcher/engagements",
        headers=headers
    )
    
    print(f"Status: {engagements_response.status_code}")
    
    if engagements_response.status_code == 200:
        engagements = engagements_response.json()
        print(f"✅ Found {len(engagements)} engagements")
        
        if engagements:
            print("\nEngagement Details:")
            for eng in engagements:
                print(f"  - {eng['name']} (Status: {eng['status']})")
                print(f"    ID: {eng['id']}")
                print(f"    Methodology: {eng['testing_methodology']}")
                print(f"    Team Size: {eng['team_size']}")
                print(f"    Assigned Researchers: {len(eng.get('assigned_researchers', []))}")
        else:
            print("ℹ️  No engagements assigned to this researcher")
    else:
        print(f"❌ Failed to fetch engagements")
        print(engagements_response.text)
    
    # Test: Get specific engagement (if any exist)
    if engagements_response.status_code == 200:
        engagements = engagements_response.json()
        if engagements:
            engagement_id = engagements[0]['id']
            
            print(f"\n3. Fetching engagement details for {engagement_id}...")
            detail_response = requests.get(
                f"{BASE_URL}/ptaas/researcher/engagements/{engagement_id}",
                headers=headers
            )
            
            print(f"Status: {detail_response.status_code}")
            
            if detail_response.status_code == 200:
                print("✅ Successfully fetched engagement details")
                engagement = detail_response.json()
                print(f"  Name: {engagement['name']}")
                print(f"  Description: {engagement['description'][:100]}...")
            else:
                print(f"❌ Failed to fetch engagement details")
                print(detail_response.text)
            
            # Test: Accept engagement
            print(f"\n4. Testing accept engagement...")
            accept_response = requests.post(
                f"{BASE_URL}/ptaas/researcher/engagements/{engagement_id}/accept",
                headers=headers
            )
            
            print(f"Status: {accept_response.status_code}")
            
            if accept_response.status_code == 200:
                print("✅ Successfully accepted engagement")
                print(accept_response.json())
            else:
                print(f"ℹ️  Accept response: {accept_response.status_code}")
                print(accept_response.text)
    
    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)

if __name__ == "__main__":
    test_researcher_endpoints()
