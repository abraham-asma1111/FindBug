#!/usr/bin/env python3
"""
Test script for duplicate marking workflow.

This script tests the complete duplicate marking flow:
1. Create two test reports
2. Mark one as duplicate of the other
3. Verify the duplicate appears on the duplicates page
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8002"

def login_as_triage():
    """Login as triage specialist."""
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": "triage@test.com",
            "password": "password123"
        }
    )
    if response.status_code == 200:
        data = response.json()
        return data.get("access_token")
    else:
        print(f"Login failed: {response.status_code}")
        print(response.text)
        return None

def get_reports(token):
    """Get all reports."""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/triage/queue?limit=100",
        headers=headers
    )
    if response.status_code == 200:
        return response.json().get("reports", [])
    else:
        print(f"Failed to get reports: {response.status_code}")
        print(response.text)
        return []

def mark_as_duplicate(token, report_id, original_id):
    """Mark a report as duplicate."""
    headers = {"Authorization": f"Bearer {token}"}
    
    # First, update status to 'triaged' if it's 'new'
    print(f"\n1. Checking report status...")
    report_response = requests.get(
        f"{BASE_URL}/reports/{report_id}",
        headers=headers
    )
    if report_response.status_code == 200:
        report = report_response.json()
        print(f"   Current status: {report.get('status')}")
        
        if report.get('status') == 'new':
            print(f"   Updating status to 'triaged' first...")
            update_response = requests.post(
                f"{BASE_URL}/triage/reports/{report_id}/update",
                headers=headers,
                json={"status": "triaged"}
            )
            if update_response.status_code == 200:
                print(f"   ✓ Status updated to 'triaged'")
            else:
                print(f"   ✗ Failed to update status: {update_response.status_code}")
                print(f"   {update_response.text}")
                return False
    
    # Now mark as duplicate
    print(f"\n2. Marking as duplicate...")
    print(f"   Report ID: {report_id}")
    print(f"   Original ID: {original_id}")
    
    payload = {
        "status": "triaged",  # Current status
        "is_duplicate": True,
        "duplicate_of": original_id
    }
    
    print(f"   Payload: {json.dumps(payload, indent=2)}")
    
    response = requests.post(
        f"{BASE_URL}/triage/reports/{report_id}/update",
        headers=headers,
        json=payload
    )
    
    if response.status_code == 200:
        print(f"   ✓ Successfully marked as duplicate")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
        return True
    else:
        print(f"   ✗ Failed to mark as duplicate: {response.status_code}")
        print(f"   {response.text}")
        return False

def verify_duplicate(token, report_id):
    """Verify the report is marked as duplicate."""
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"\n3. Verifying duplicate marking...")
    response = requests.get(
        f"{BASE_URL}/reports/{report_id}",
        headers=headers
    )
    
    if response.status_code == 200:
        report = response.json()
        print(f"   Status: {report.get('status')}")
        print(f"   Is Duplicate: {report.get('is_duplicate')}")
        print(f"   Duplicate Of: {report.get('duplicate_of')}")
        
        if report.get('is_duplicate') and report.get('duplicate_of'):
            print(f"   ✓ Report correctly marked as duplicate")
            return True
        else:
            print(f"   ✗ Report NOT marked as duplicate")
            return False
    else:
        print(f"   ✗ Failed to get report: {response.status_code}")
        return False

def check_duplicates_page(token):
    """Check if duplicates appear on the duplicates page."""
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"\n4. Checking duplicates page...")
    response = requests.get(
        f"{BASE_URL}/triage/queue?limit=100",
        headers=headers
    )
    
    if response.status_code == 200:
        reports = response.json().get("reports", [])
        duplicates = [r for r in reports if r.get('is_duplicate')]
        
        print(f"   Total reports: {len(reports)}")
        print(f"   Duplicate reports: {len(duplicates)}")
        
        if duplicates:
            print(f"\n   Duplicate reports found:")
            for dup in duplicates:
                print(f"   - {dup.get('report_number')}: {dup.get('title')}")
                print(f"     Duplicate of: {dup.get('duplicate_of')}")
                print(f"     Status: {dup.get('status')}")
            return True
        else:
            print(f"   ✗ No duplicate reports found")
            return False
    else:
        print(f"   ✗ Failed to get queue: {response.status_code}")
        return False

def main():
    print("=" * 60)
    print("DUPLICATE MARKING WORKFLOW TEST")
    print("=" * 60)
    
    # Login
    print("\n[Step 1] Logging in as triage specialist...")
    token = login_as_triage()
    if not token:
        print("✗ Login failed. Exiting.")
        return
    print("✓ Login successful")
    
    # Get reports
    print("\n[Step 2] Getting reports...")
    reports = get_reports(token)
    if len(reports) < 2:
        print(f"✗ Need at least 2 reports, found {len(reports)}. Exiting.")
        return
    
    print(f"✓ Found {len(reports)} reports")
    print(f"\nFirst 5 reports:")
    for i, report in enumerate(reports[:5]):
        print(f"  {i+1}. {report.get('report_number')}: {report.get('title')}")
        print(f"     Status: {report.get('status')}, Is Duplicate: {report.get('is_duplicate')}")
    
    # Select two reports for testing
    original_report = reports[0]
    duplicate_report = reports[1]
    
    print(f"\n[Step 3] Testing duplicate marking...")
    print(f"Original: {original_report.get('report_number')} - {original_report.get('title')}")
    print(f"Duplicate: {duplicate_report.get('report_number')} - {duplicate_report.get('title')}")
    
    # Mark as duplicate
    success = mark_as_duplicate(
        token,
        duplicate_report.get('id'),
        original_report.get('id')
    )
    
    if not success:
        print("\n✗ Failed to mark as duplicate. Exiting.")
        return
    
    # Verify
    if verify_duplicate(token, duplicate_report.get('id')):
        print("\n✓ Duplicate marking verified")
    else:
        print("\n✗ Duplicate marking verification failed")
        return
    
    # Check duplicates page
    if check_duplicates_page(token):
        print("\n✓ Duplicates appear on duplicates page")
    else:
        print("\n✗ Duplicates do NOT appear on duplicates page")
        return
    
    print("\n" + "=" * 60)
    print("✓ ALL TESTS PASSED")
    print("=" * 60)

if __name__ == "__main__":
    main()
