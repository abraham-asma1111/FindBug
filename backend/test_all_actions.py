#!/usr/bin/env python3
"""Test all report actions: View, Edit (placeholder), Delete."""
import requests
import sys

BASE_URL = "http://localhost:8002/api/v1"

# Login as researcher
print("=== Logging in as researcher ===")
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={
        "email": "researcher@test.com",
        "password": "Password123!"
    }
)

if login_response.status_code != 200:
    print(f"✗ Login failed: {login_response.status_code}")
    print(login_response.text)
    sys.exit(1)

print("✓ Login successful")
token = login_response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Get list of reports
print("\n=== Getting report list ===")
reports_response = requests.get(
    f"{BASE_URL}/reports/my-reports",
    headers=headers
)

if reports_response.status_code != 200:
    print(f"✗ Failed to get reports: {reports_response.status_code}")
    print(reports_response.text)
    sys.exit(1)

reports = reports_response.json()
print(f"✓ Found {len(reports)} reports")

if len(reports) == 0:
    print("No reports to test with")
    sys.exit(0)

# Find a report with status "new" for testing
new_report = None
for report in reports:
    if report["status"] == "new":
        new_report = report
        break

if not new_report:
    print("No reports with status 'new' found for testing")
    new_report = reports[0]  # Use first report anyway

report_id = new_report["id"]
print(f"\nTesting with report: {report_id}")
print(f"  Title: {new_report['title']}")
print(f"  Status: {new_report['status']}")

# TEST 1: View Report
print("\n=== TEST 1: View Report ===")
view_response = requests.get(
    f"{BASE_URL}/reports/{report_id}",
    headers=headers
)

print(f"Status: {view_response.status_code}")
if view_response.status_code == 200:
    report_detail = view_response.json()
    print(f"✓ View successful")
    print(f"  Report Number: {report_detail.get('report_number', 'N/A')}")
    print(f"  Program: {report_detail.get('program', {}).get('name', 'N/A')}")
else:
    print(f"✗ View failed")
    print(f"  Response: {view_response.text}")

# TEST 2: Update Report (only if status is "new")
if new_report["status"] == "new":
    print("\n=== TEST 2: Update Report ===")
    update_response = requests.put(
        f"{BASE_URL}/reports/{report_id}",
        headers=headers,
        json={
            "title": new_report["title"] + " (Updated)",
            "description": new_report.get("description", "Test description")
        }
    )
    
    print(f"Status: {update_response.status_code}")
    if update_response.status_code == 200:
        print(f"✓ Update successful")
    else:
        print(f"✗ Update failed")
        print(f"  Response: {update_response.text}")
else:
    print(f"\n=== TEST 2: Update Report ===")
    print(f"⊘ Skipped (report status is '{new_report['status']}', not 'new')")

# TEST 3: Delete Report (only if status is "new")
# Note: We'll use a different report if available to avoid deleting the one we just updated
delete_report = None
for report in reports:
    if report["status"] == "new" and report["id"] != report_id:
        delete_report = report
        break

if delete_report:
    print("\n=== TEST 3: Delete Report ===")
    delete_id = delete_report["id"]
    print(f"Deleting report: {delete_id}")
    
    delete_response = requests.delete(
        f"{BASE_URL}/reports/{delete_id}",
        headers=headers
    )
    
    print(f"Status: {delete_response.status_code}")
    if delete_response.status_code in [200, 204]:
        print(f"✓ Delete successful")
        
        # Verify it's deleted
        verify_response = requests.get(
            f"{BASE_URL}/reports/my-reports",
            headers=headers
        )
        if verify_response.status_code == 200:
            remaining_reports = verify_response.json()
            if delete_id not in [r["id"] for r in remaining_reports]:
                print(f"✓ Verified: Report no longer in list")
            else:
                print(f"⚠ Warning: Report still appears in list")
    else:
        print(f"✗ Delete failed")
        print(f"  Response: {delete_response.text}")
else:
    print(f"\n=== TEST 3: Delete Report ===")
    print(f"⊘ Skipped (no additional 'new' reports available for deletion test)")

print("\n=== All tests complete ===")
