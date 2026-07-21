"""
Test bounty approval status update workflow.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import requests
import json

def test_bounty_approval_status():
    """Test that bounty approval updates the report status correctly."""
    
    print("\n" + "="*80)
    print("BOUNTY APPROVAL STATUS UPDATE TEST")
    print("="*80)
    
    # Login as organization
    print("\n[1] Logging in as organization...")
    login_response = requests.post(
        "http://127.0.0.1:8002/api/v1/auth/login",
        json={
            "email": "org@test.com",
            "password": "Password123!"
        }
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(login_response.text)
        return
    
    token = login_response.json()["access_token"]
    print(f"✅ Login successful")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get a valid report
    print("\n[2] Finding a valid report...")
    reports_response = requests.get(
        "http://127.0.0.1:8002/api/v1/reports?status_filter=valid&limit=1",
        headers=headers
    )
    
    if reports_response.status_code != 200:
        print(f"❌ Failed to get reports: {reports_response.status_code}")
        return
    
    reports = reports_response.json().get("reports", [])
    if not reports:
        print("❌ No valid reports found")
        return
    
    report = reports[0]
    report_id = report["id"]
    print(f"✅ Found report: {report['report_number']}")
    print(f"   Status: {report['status']}")
    print(f"   Bounty: {report.get('bounty_amount', 0)} ETB")
    print(f"   Bounty Status: {report.get('bounty_status', 'None')}")
    
    # Get full report details BEFORE approval
    print("\n[3] Getting report details BEFORE approval...")
    report_detail_response = requests.get(
        f"http://127.0.0.1:8002/api/v1/reports/{report_id}",
        headers=headers
    )
    
    if report_detail_response.status_code == 200:
        report_before = report_detail_response.json()
        print(f"✅ Report details retrieved")
        print(f"   Bounty Status BEFORE: {report_before.get('bounty_status', 'None')}")
    else:
        print(f"❌ Failed to get report details: {report_detail_response.status_code}")
        return
    
    # Check if already approved
    if report_before.get('bounty_status') == 'approved':
        print("\n⚠️  Bounty already approved for this report")
        print("   Skipping approval test")
        return
    
    # Approve bounty
    print("\n[4] Approving bounty...")
    approval_response = requests.post(
        f"http://127.0.0.1:8002/api/v1/reports/{report_id}/approve-bounty",
        headers=headers
    )
    
    print(f"Status: {approval_response.status_code}")
    
    if approval_response.status_code == 200:
        approval_data = approval_response.json()
        print(f"✅ Bounty approved successfully")
        print(f"   Payment ID: {approval_data.get('payment_id')}")
        print(f"   Bounty Amount: {approval_data.get('bounty_amount')} ETB")
        print(f"   Commission: {approval_data.get('commission')} ETB")
        print(f"   Total Cost: {approval_data.get('total_cost')} ETB")
    elif approval_response.status_code == 400:
        error_detail = approval_response.json().get('detail', '')
        if 'already been approved' in error_detail:
            print(f"⚠️  Bounty already approved")
            print("   This is expected if running the test multiple times")
        else:
            print(f"❌ Approval failed: {error_detail}")
            return
    else:
        print(f"❌ Approval failed: {approval_response.status_code}")
        print(approval_response.text)
        return
    
    # Get full report details AFTER approval
    print("\n[5] Getting report details AFTER approval...")
    report_detail_response = requests.get(
        f"http://127.0.0.1:8002/api/v1/reports/{report_id}",
        headers=headers
    )
    
    if report_detail_response.status_code == 200:
        report_after = report_detail_response.json()
        print(f"✅ Report details retrieved")
        print(f"   Bounty Status AFTER: {report_after.get('bounty_status', 'None')}")
        
        # Verify the status changed
        if report_after.get('bounty_status') == 'approved':
            print(f"\n✅ SUCCESS: Bounty status correctly updated to 'approved'")
        else:
            print(f"\n❌ FAILED: Bounty status is '{report_after.get('bounty_status')}', expected 'approved'")
    else:
        print(f"❌ Failed to get report details: {report_detail_response.status_code}")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    test_bounty_approval_status()
