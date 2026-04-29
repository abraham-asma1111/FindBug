#!/usr/bin/env python3
"""
Test the new triage valid reports by severity endpoint.
"""
import requests
import json

BASE_URL = "http://localhost:8002/api/v1"

# Login as finance officer
login_data = {
    "email": "finance@securecrowd.com",
    "password": "Finance123!@#"
}

print("Logging in as finance officer...")
response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
if response.status_code != 200:
    print(f"Login failed: {response.status_code}")
    print(response.text)
    exit(1)

token = response.json()["access_token"]
print(f"✓ Login successful")

# Test the new endpoint
headers = {"Authorization": f"Bearer {token}"}
print("\nFetching valid reports by severity...")
response = requests.get(f"{BASE_URL}/triage/valid-reports-by-severity", headers=headers)

if response.status_code != 200:
    print(f"Request failed: {response.status_code}")
    print(response.text)
    exit(1)

data = response.json()
print(f"\n{'='*80}")
print(f"VALID REPORTS BY SEVERITY (API Response)")
print(f"{'='*80}\n")
print(json.dumps(data, indent=2))

print(f"\n{'='*80}")
print(f"Total Valid Reports: {data['total']}")
print(f"{'='*80}\n")

for item in data['by_severity']:
    severity = item['severity']
    count = item['count']
    percentage = item['percentage']
    
    # Color coding
    if severity == 'critical':
        icon = '🔴'
    elif severity == 'high':
        icon = '🟠'
    elif severity == 'medium':
        icon = '🟡'
    elif severity == 'low':
        icon = '🟢'
    else:
        icon = '⚪'
    
    print(f"{icon} {severity.upper():15} : {count:3} reports ({percentage:5.1f}%)")

print(f"\n✓ Endpoint working correctly!")
