#!/usr/bin/env python3
"""
Test organization viewing reports via API
"""

import requests
import json

BASE_URL = "http://localhost:8002/api/v1"

# Login as organization
print("1. Logging in as organization...")
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={
        "email": "org@example.com",
        "password": "password123"
    }
)

if login_response.status_code != 200:
    print(f"❌ Login failed: {login_response.text}")
    exit(1)

token = login_response.json()["access_token"]
print(f"✅ Logged in successfully")

headers = {"Authorization": f"Bearer {token}"}

# Get engagements
print("\n2. Fetching engagements...")
engagements_response = requests.get(
    f"{BASE_URL}/ai-red-teaming/engagements",
    headers=headers
)

if engagements_response.status_code != 200:
    print(f"❌ Failed to fetch engagements: {engagements_response.text}")
    exit(1)

engagements = engagements_response.json()
print(f"✅ Found {len(engagements)} engagement(s)")

# Find "chat gpt" engagement
chat_gpt_engagement = None
for eng in engagements:
    print(f"   - {eng['name']} (ID: {eng['id']}, Status: {eng['status']})")
    if eng['name'] == 'chat gpt':
        chat_gpt_engagement = eng

if not chat_gpt_engagement:
    print("\n❌ 'chat gpt' engagement not found!")
    exit(1)

engagement_id = chat_gpt_engagement['id']
print(f"\n3. Testing reports endpoint for engagement: {engagement_id}")

# Get reports for this engagement
reports_response = requests.get(
    f"{BASE_URL}/ai-red-teaming/engagements/{engagement_id}/reports",
    headers=headers
)

print(f"\nStatus Code: {reports_response.status_code}")
print(f"Response Headers: {dict(reports_response.headers)}")

if reports_response.status_code == 200:
    reports = reports_response.json()
    print(f"\n✅ SUCCESS! Found {len(reports)} report(s)")
    
    if reports:
        print("\nReport Details:")
        for report in reports:
            print(json.dumps(report, indent=2))
    else:
        print("\n⚠️  No reports returned (but API call succeeded)")
else:
    print(f"\n❌ Failed to fetch reports:")
    print(f"Status: {reports_response.status_code}")
    print(f"Response: {reports_response.text}")

# Also test the engagement detail endpoint
print(f"\n4. Testing engagement detail endpoint...")
detail_response = requests.get(
    f"{BASE_URL}/ai-red-teaming/engagements/{engagement_id}",
    headers=headers
)

if detail_response.status_code == 200:
    detail = detail_response.json()
    print(f"✅ Engagement details retrieved")
    print(f"   Total Findings: {detail.get('total_findings', 0)}")
    print(f"   Critical Findings: {detail.get('critical_findings', 0)}")
else:
    print(f"❌ Failed to get engagement details: {detail_response.text}")
