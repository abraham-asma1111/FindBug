#!/usr/bin/env python3
"""
Test script for duplicate detection workflow.
Tests the complete flow of marking reports as duplicates.
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8002/api/v1"

def login(email, password):
    """Login and get access token"""
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": email, "password": password}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Login failed: {response.status_code}")
        print(response.text)
        return None

def get_headers(token):
    """Get authorization headers"""
    return {"Authorization": f"Bearer {token}"}

def test_duplicate_workflow():
    """Test the complete duplicate workflow"""
    
    print("=" * 80)
    print("DUPLICATE DETECTION WORKFLOW TEST")
    print("=" * 80)
    
    # Step 1: Login as triage specialist
    print("\n1. Logging in as triage specialist...")
    token = login("triage@example.com", "password123")
    if not token:
        print("❌ Failed to login")
        return
    print("✅ Logged in successfully")
    
    headers = get_headers(token)
    
    # Step 2: Get all reports
    print("\n2. Fetching all reports...")
    response = requests.get(f"{BASE_URL}/triage/queue?limit=100", headers=headers)
    if response.status_code != 200:
        print(f"❌ Failed to fetch reports: {response.status_code}")
        print(response.text)
        return
    
    reports = response.json()["reports"]
    print(f"✅ Found {len(reports)} reports")
    
    # Find reports with same title
    print("\n3. Looking for duplicate reports (same title)...")
    title_groups = {}
    for report in reports:
        title = report["title"]
        if title not in title_groups:
            title_groups[title] = []
        title_groups[title].append(report)
    
    duplicate_candidates = {title: reps for title, reps in title_groups.items() if len(reps) > 1}
    
    if not duplicate_candidates:
        print("❌ No duplicate candidates found. Please submit 2 reports with the same title from different researchers.")
        return
    
    print(f"✅ Found {len(duplicate_candidates)} potential duplicate groups:")
    for title, reps in duplicate_candidates.items():
        print(f"\n   Title: '{title}'")
        for rep in reps:
            print(f"   - Report #{rep['report_number']} by researcher {rep.get('researcher_id', 'Unknown')}")
            print(f"     Status: {rep['status']}, Submitted: {rep.get('submitted_at', 'N/A')}")
    
    # Step 4: Test "Find Similar Reports" for each duplicate candidate
    print("\n4. Testing 'Find Similar Reports' endpoint...")
    for title, reps in duplicate_candidates.items():
        if len(reps) < 2:
            continue
            
        print(f"\n   Testing with title: '{title}'")
        second_report = reps[1]  # Use the second report
        report_id = second_report["id"]
        
        print(f"   Searching for similar reports to: {second_report['report_number']}")
        response = requests.get(
            f"{BASE_URL}/triage/reports/{report_id}/similar?limit=10",
            headers=headers
        )
        
        if response.status_code != 200:
            print(f"   ❌ Failed to find similar reports: {response.status_code}")
            print(f"   {response.text}")
            continue
        
        similar = response.json()
        print(f"   ✅ Found {similar['total']} similar reports:")
        for sim in similar.get('similar_reports', []):
            print(f"      - {sim.get('report_number', 'N/A')}: {sim.get('title', 'N/A')}")
            print(f"        Researcher: {sim.get('researcher_username', 'Unknown')}")
            print(f"        Status: {sim.get('status', 'N/A')}")
        
        # Step 5: Try to mark as duplicate
        if similar['total'] > 0:
            print(f"\n5. Attempting to mark report as duplicate...")
            original_report = similar['similar_reports'][0]
            
            update_payload = {
                "status": "duplicate",
                "is_duplicate": True,
                "duplicate_of": original_report['id']
            }
            
            print(f"   Marking {second_report['report_number']} as duplicate of {original_report['report_number']}")
            print(f"   Payload: {json.dumps(update_payload, indent=2)}")
            
            response = requests.post(
                f"{BASE_URL}/triage/reports/{report_id}/update",
                headers=headers,
                json=update_payload
            )
            
            if response.status_code == 200:
                print(f"   ✅ Successfully marked as duplicate!")
                result = response.json()
                print(f"   Result: {json.dumps(result, indent=2)}")
            else:
                print(f"   ❌ Failed to mark as duplicate: {response.status_code}")
                print(f"   {response.text}")
            
            # Step 6: Verify on duplicates page
            print(f"\n6. Verifying on duplicates page...")
            response = requests.get(f"{BASE_URL}/triage/queue?limit=100", headers=headers)
            if response.status_code == 200:
                updated_reports = response.json()["reports"]
                duplicate_reports = [r for r in updated_reports if r.get('is_duplicate')]
                print(f"   ✅ Total duplicate reports in system: {len(duplicate_reports)}")
                for dup in duplicate_reports:
                    print(f"      - {dup['report_number']}: duplicate_of={dup.get('duplicate_of', 'None')}")
            
            break  # Only test first group
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    test_duplicate_workflow()
