#!/usr/bin/env python3
"""
Test script for triage endpoints - debugging 400 errors.

This script tests:
1. Report update endpoint (POST /triage/reports/{id}/update)
2. Bulk action endpoint (POST /triage/researchers/{id}/reports/bulk-action)
"""

import requests
import json
from uuid import UUID

# Configuration
API_URL = "http://127.0.0.1:8002/api/v1"
TRIAGE_EMAIL = "triage@example.com"
TRIAGE_PASSWORD = "password123"

def login():
    """Login and get access token."""
    print("=== Logging in as triage specialist ===")
    response = requests.post(
        f"{API_URL}/auth/login",
        json={
            "email": TRIAGE_EMAIL,
            "password": TRIAGE_PASSWORD
        }
    )
    
    if response.status_code != 200:
        print(f"Login failed: {response.status_code}")
        print(response.text)
        return None
    
    data = response.json()
    token = data.get("access_token")
    print(f"Login successful! Token: {token[:20]}...")
    return token


def test_report_update(token: str, report_id: str):
    """Test report update endpoint."""
    print(f"\n=== Testing Report Update ===")
    print(f"Report ID: {report_id}")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test payload - minimal valid data
    payload = {
        "status": "triaged",
        "assigned_severity": "high",
        "triage_notes": "Test update from script"
    }
    
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    response = requests.post(
        f"{API_URL}/triage/reports/{report_id}/update",
        headers=headers,
        json=payload
    )
    
    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.text}")
    
    if response.status_code == 200:
        print("✓ Report update successful!")
        return True
    else:
        print("✗ Report update failed!")
        return False


def test_bulk_action(token: str, researcher_id: str, report_ids: list):
    """Test bulk action endpoint."""
    print(f"\n=== Testing Bulk Action ===")
    print(f"Researcher ID: {researcher_id}")
    print(f"Report IDs: {report_ids}")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Build URL with query parameters
    url = f"{API_URL}/triage/researchers/{researcher_id}/reports/bulk-action?action=mark_invalid"
    
    print(f"URL: {url}")
    print(f"Body: {json.dumps(report_ids, indent=2)}")
    
    response = requests.post(
        url,
        headers=headers,
        json=report_ids
    )
    
    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.text}")
    
    if response.status_code == 200:
        print("✓ Bulk action successful!")
        return True
    else:
        print("✗ Bulk action failed!")
        return False


def get_first_report(token: str):
    """Get the first report from the queue."""
    print("\n=== Getting first report from queue ===")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(
        f"{API_URL}/triage/queue?limit=1",
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"Failed to get queue: {response.status_code}")
        return None, None
    
    data = response.json()
    reports = data.get("reports", [])
    
    if not reports:
        print("No reports in queue")
        return None, None
    
    report = reports[0]
    report_id = report["id"]
    researcher_id = report.get("researcher_id")
    
    print(f"Found report: {report_id}")
    print(f"Researcher: {researcher_id}")
    
    return report_id, researcher_id


def get_researcher_reports(token: str, researcher_id: str):
    """Get reports from a researcher."""
    print(f"\n=== Getting reports from researcher {researcher_id} ===")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(
        f"{API_URL}/triage/researchers/{researcher_id}/reports?limit=5",
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"Failed to get researcher reports: {response.status_code}")
        return []
    
    data = response.json()
    reports = data.get("reports", [])
    report_ids = [r["id"] for r in reports]
    
    print(f"Found {len(report_ids)} reports")
    return report_ids


def main():
    """Run all tests."""
    print("=" * 60)
    print("TRIAGE ENDPOINTS TEST SCRIPT")
    print("=" * 60)
    
    # Login
    token = login()
    if not token:
        print("Cannot proceed without token")
        return
    
    # Get a report to test with
    report_id, researcher_id = get_first_report(token)
    if not report_id:
        print("Cannot proceed without a report")
        return
    
    # Test 1: Report Update
    print("\n" + "=" * 60)
    print("TEST 1: Report Update Endpoint")
    print("=" * 60)
    test_report_update(token, report_id)
    
    # Test 2: Bulk Action
    if researcher_id:
        print("\n" + "=" * 60)
        print("TEST 2: Bulk Action Endpoint")
        print("=" * 60)
        
        # Get some reports from this researcher
        report_ids = get_researcher_reports(token, researcher_id)
        
        if report_ids:
            # Test with first 2 reports
            test_bulk_action(token, researcher_id, report_ids[:2])
        else:
            print("No reports found for bulk action test")
    
    print("\n" + "=" * 60)
    print("TESTS COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
