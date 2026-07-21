#!/usr/bin/env python3
"""Test viewing a report with detailed error output."""
import requests
import sys
import json

BASE_URL = "http://localhost:8002/api/v1"

# Login as researcher
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={
        "email": "researcher@test.com",
        "password": "Password123!"
    }
)

if login_response.status_code != 200:
    print(f"Login failed: {login_response.status_code}")
    print(login_response.text)
    sys.exit(1)

token = login_response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Get list of reports
reports_response = requests.get(
    f"{BASE_URL}/reports/my-reports",
    headers=headers
)

if reports_response.status_code != 200:
    print(f"Failed to get reports: {reports_response.status_code}")
    print(reports_response.text)
    sys.exit(1)

reports = reports_response.json()
print(f"Found {len(reports)} reports")

if len(reports) == 0:
    print("No reports to test with")
    sys.exit(0)

# Try to view the first report
report_id = reports[0]["id"]
print(f"\nTrying to view report: {report_id}")

view_response = requests.get(
    f"{BASE_URL}/reports/{report_id}",
    headers=headers
)

print(f"Status: {view_response.status_code}")
print(f"Response: {view_response.text}")

if view_response.status_code == 200:
    report = view_response.json()
    print(f"\n✓ Successfully viewed report")
    print(json.dumps(report, indent=2))
else:
    print(f"\n✗ Failed to view report")
