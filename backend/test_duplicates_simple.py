#!/usr/bin/env python3
"""
Simple test to check duplicate marking and viewing.
Run this after marking reports as duplicates.
"""

import requests

BASE_URL = "http://localhost:8002/api/v1"

# Login
response = requests.post(
    f"{BASE_URL}/auth/login",
    json={"email": "triage@example.com", "password": "password123"}
)
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Get all reports
print("Fetching all reports...")
response = requests.get(f"{BASE_URL}/triage/queue?limit=100", headers=headers)
reports = response.json()["reports"]

print(f"\nTotal reports: {len(reports)}")
print("\nReports with is_duplicate=True:")
for report in reports:
    if report.get('is_duplicate'):
        print(f"  - {report['report_number']}: {report['title']}")
        print(f"    duplicate_of: {report.get('duplicate_of')}")
        print(f"    status: {report['status']}")
        print(f"    researcher_id: {report.get('researcher_id')}")
        print()

# Count duplicates
duplicate_count = sum(1 for r in reports if r.get('is_duplicate'))
print(f"Total duplicates found: {duplicate_count}")

if duplicate_count == 0:
    print("\n⚠️  No duplicates found!")
    print("Steps to create duplicates:")
    print("1. Submit 2 reports with same title from 2 different researchers")
    print("2. Login to triage portal")
    print("3. Open the second report")
    print("4. Check 'Mark as Duplicate'")
    print("5. Click 'Find Similar Reports'")
    print("6. Click on the first report to select it")
    print("7. Set Status to 'duplicate'")
    print("8. Click 'Save Changes'")
