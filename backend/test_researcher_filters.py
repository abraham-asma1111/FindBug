#!/usr/bin/env python3
"""Test researcher reports filtering."""
import requests
import json

BASE_URL = "http://localhost:8002/api/v1"

# Login as triage specialist
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={
        "email": "triage@example.com",
        "password": "password123"
    }
)

if login_response.status_code != 200:
    print(f"Login failed: {login_response.status_code}")
    print(login_response.text)
    exit(1)

token = login_response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Get list of researchers first
print("\n=== Getting Researchers List ===")
researchers_response = requests.get(
    f"{BASE_URL}/triage/researchers",
    headers=headers
)

if researchers_response.status_code != 200:
    print(f"Failed to get researchers: {researchers_response.status_code}")
    print(researchers_response.text)
    exit(1)

researchers = researchers_response.json()["researchers"]
print(f"Found {len(researchers)} researchers")

if len(researchers) == 0:
    print("No researchers found!")
    exit(1)

# Pick first researcher
researcher = researchers[0]
researcher_id = researcher["id"]
print(f"\nTesting with researcher: {researcher['username']} ({researcher['email']})")
print(f"Total reports: {researcher['total_reports']}")

# Test 1: Get all reports (no filter)
print("\n=== Test 1: All Reports (No Filter) ===")
all_reports_response = requests.get(
    f"{BASE_URL}/triage/researchers/{researcher_id}/reports",
    headers=headers
)

if all_reports_response.status_code != 200:
    print(f"Failed: {all_reports_response.status_code}")
    print(all_reports_response.text)
else:
    all_reports = all_reports_response.json()
    print(f"Total reports: {all_reports['total']}")
    print(f"Reports returned: {len(all_reports['reports'])}")
    
    # Show status breakdown
    statuses = {}
    for report in all_reports['reports']:
        status = report['status']
        statuses[status] = statuses.get(status, 0) + 1
    print(f"Status breakdown: {statuses}")

# Test 2: Filter by status = 'valid'
print("\n=== Test 2: Filter by Status = 'valid' ===")
valid_reports_response = requests.get(
    f"{BASE_URL}/triage/researchers/{researcher_id}/reports?status_filter=valid",
    headers=headers
)

if valid_reports_response.status_code != 200:
    print(f"Failed: {valid_reports_response.status_code}")
    print(valid_reports_response.text)
else:
    valid_reports = valid_reports_response.json()
    print(f"Total reports: {valid_reports['total']}")
    print(f"Reports returned: {len(valid_reports['reports'])}")
    
    # Verify all are valid
    all_valid = all(r['status'] == 'valid' for r in valid_reports['reports'])
    print(f"All reports have status='valid': {all_valid}")

# Test 3: Filter by status = 'new'
print("\n=== Test 3: Filter by Status = 'new' ===")
new_reports_response = requests.get(
    f"{BASE_URL}/triage/researchers/{researcher_id}/reports?status_filter=new",
    headers=headers
)

if new_reports_response.status_code != 200:
    print(f"Failed: {new_reports_response.status_code}")
    print(new_reports_response.text)
else:
    new_reports = new_reports_response.json()
    print(f"Total reports: {new_reports['total']}")
    print(f"Reports returned: {len(new_reports['reports'])}")
    
    # Verify all are new
    all_new = all(r['status'] == 'new' for r in new_reports['reports'])
    print(f"All reports have status='new': {all_new}")

# Test 4: Show duplicates only
print("\n=== Test 4: Duplicates Only ===")
dup_reports_response = requests.get(
    f"{BASE_URL}/triage/researchers/{researcher_id}/reports?show_duplicates_only=true",
    headers=headers
)

if dup_reports_response.status_code != 200:
    print(f"Failed: {dup_reports_response.status_code}")
    print(dup_reports_response.text)
else:
    dup_reports = dup_reports_response.json()
    print(f"Total reports: {dup_reports['total']}")
    print(f"Reports returned: {len(dup_reports['reports'])}")
    
    # Verify all are duplicates
    all_dup = all(r['is_duplicate'] for r in dup_reports['reports'])
    print(f"All reports have is_duplicate=True: {all_dup}")

# Test 5: Combine filters (status=valid AND duplicates_only)
print("\n=== Test 5: Status='valid' AND Duplicates Only ===")
combined_response = requests.get(
    f"{BASE_URL}/triage/researchers/{researcher_id}/reports?status_filter=valid&show_duplicates_only=true",
    headers=headers
)

if combined_response.status_code != 200:
    print(f"Failed: {combined_response.status_code}")
    print(combined_response.text)
else:
    combined_reports = combined_response.json()
    print(f"Total reports: {combined_reports['total']}")
    print(f"Reports returned: {len(combined_reports['reports'])}")
    
    # Verify all match both filters
    all_match = all(r['status'] == 'valid' and r['is_duplicate'] for r in combined_reports['reports'])
    print(f"All reports match both filters: {all_match}")

print("\n=== Test Complete ===")
