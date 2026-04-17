"""
Test the researcher engagement list API endpoint
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def login_researcher():
    """Login as researcher"""
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": "newresearcher@example.com",
            "password": "password123"
        }
    )
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Logged in as researcher")
        return data.get("access_token")
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(response.text)
        return None

def list_engagements(token):
    """List researcher engagements"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/ptaas/researcher/engagements",
        headers=headers
    )
    
    print(f"\n📊 GET /ptaas/researcher/engagements")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        engagements = response.json()
        print(f"✅ Found {len(engagements)} engagement(s)")
        for eng in engagements:
            print(f"\n  Engagement: {eng['name']}")
            print(f"  ID: {eng['id']}")
            print(f"  Status: {eng['status']}")
            print(f"  Methodology: {eng['testing_methodology']}")
            print(f"  Assigned Researchers: {eng.get('assigned_researchers', [])}")
    else:
        print(f"❌ Failed to list engagements")
        print(response.text)

if __name__ == "__main__":
    token = login_researcher()
    if token:
        list_engagements(token)
