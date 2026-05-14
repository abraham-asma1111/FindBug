#!/usr/bin/env python3
"""Test finance program detail endpoint with enriched stats."""

import requests
import json

BASE_URL = "http://localhost:8002/api/v1"

# Login as finance officer
login_data = {
    "email": "finance@findbug.com",
    "password": "Finance123!"
}

print("🔐 Logging in as finance officer...")
response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
if response.status_code != 200:
    print(f"❌ Login failed: {response.status_code}")
    print(response.text)
    exit(1)

token = response.json()["access_token"]
print(f"✅ Login successful! Token: {token[:50]}...")

headers = {"Authorization": f"Bearer {token}"}

# Test program ID from logs
program_id = "ade9b88b-d3e2-444b-9546-fdf9eac0a273"

print(f"\n📊 Testing GET /programs/{program_id}?enrich_stats=true")
response = requests.get(
    f"{BASE_URL}/programs/{program_id}?enrich_stats=true",
    headers=headers
)

print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print("\n✅ Program details with enriched stats:")
    print(json.dumps(data, indent=2))
    
    # Check if stats are present
    stats_fields = [
        'total_reports', 'valid_reports', 'total_researchers',
        'researchers_with_reports', 'total_bounties_paid', 'pending_payments',
        'min_bounty', 'max_bounty'
    ]
    
    print("\n📈 Statistics check:")
    for field in stats_fields:
        value = data.get(field, 'MISSING')
        status = "✅" if field in data else "❌"
        print(f"{status} {field}: {value}")
else:
    print(f"❌ Request failed: {response.text}")

print(f"\n📊 Testing GET /reports?program_id={program_id}")
response = requests.get(
    f"{BASE_URL}/reports?program_id={program_id}",
    headers=headers
)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    reports = response.json()
    if isinstance(reports, list):
        print(f"✅ Found {len(reports)} reports")
        if reports:
            print(f"First report: {reports[0].get('title', 'N/A')}")
    else:
        print(f"✅ Reports data: {type(reports)}")
else:
    print(f"❌ Request failed: {response.text}")

print(f"\n📊 Testing GET /programs/{program_id}/participants")
response = requests.get(
    f"{BASE_URL}/programs/{program_id}/participants",
    headers=headers
)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    participants = response.json()
    print(f"✅ Found {len(participants)} participants")
    if participants:
        print(f"First participant: {participants[0].get('username', 'N/A')}")
else:
    print(f"❌ Request failed: {response.text}")

print("\n✅ All tests complete!")
