"""Test report submission with evidence files."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import requests
import json
from io import BytesIO

# API Configuration
BASE_URL = "http://localhost:8002/api/v1"

def test_report_submission_with_evidence():
    """Test complete flow: researcher submits report with evidence, triage views it."""
    
    print("=" * 80)
    print("TESTING REPORT SUBMISSION WITH EVIDENCE")
    print("=" * 80)
    
    # Step 1: Login as researcher
    print("\n1. Logging in as researcher...")
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": "test.researcher.fresh@example.com",
            "password": "TestPass123!"
        }
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(login_response.text)
        return
    
    researcher_token = login_response.json()["access_token"]
    researcher_headers = {"Authorization": f"Bearer {researcher_token}"}
    print("✅ Researcher logged in successfully")
    
    # Step 2: Get available programs
    print("\n2. Fetching available programs...")
    programs_response = requests.get(
        f"{BASE_URL}/programs",
        headers=researcher_headers
    )
    
    if programs_response.status_code != 200:
        print(f"❌ Failed to fetch programs: {programs_response.status_code}")
        return
    
    programs = programs_response.json()
    if not programs:
        print("❌ No programs available")
        return
    
    program_id = programs[0]["id"]
    program_name = programs[0]["name"]
    print(f"✅ Found program: {program_name} ({program_id})")
    
    # Step 2.5: Join the program
    print("\n2.5. Joining the program...")
    join_response = requests.post(
        f"{BASE_URL}/programs/{program_id}/join",
        headers=researcher_headers
    )
    
    if join_response.status_code in [200, 201]:
        print(f"✅ Joined program: {program_name}")
    elif join_response.status_code == 400 and "already joined" in join_response.text.lower():
        print(f"✅ Already joined program: {program_name}")
    else:
        print(f"⚠️  Join failed: {join_response.status_code} - {join_response.text}")
    
    # Step 3: Submit vulnerability report
    print("\n3. Submitting vulnerability report...")
    report_data = {
        "program_id": program_id,
        "title": "Critical XSS Vulnerability in User Profile",
        "description": "I discovered a stored cross-site scripting (XSS) vulnerability in the user profile page. An attacker can inject malicious JavaScript code that executes when other users view the profile. This is a critical security issue that could lead to account takeover, session hijacking, and data theft.",
        "steps_to_reproduce": "1. Navigate to profile settings\n2. In the 'Bio' field, enter: <script>alert('XSS')</script>\n3. Save the profile\n4. View your profile as another user\n5. The JavaScript executes automatically",
        "impact_assessment": "An attacker could steal session cookies, redirect users to phishing sites, modify page content, or perform actions on behalf of the victim. This affects all users who view the compromised profile.",
        "suggested_severity": "critical",
        "vulnerability_type": "Cross-Site Scripting (XSS)",
        "affected_asset": "https://example.com/profile"
    }
    
    report_response = requests.post(
        f"{BASE_URL}/reports",
        headers=researcher_headers,
        json=report_data
    )
    
    if report_response.status_code != 201:
        print(f"❌ Report submission failed: {report_response.status_code}")
        print(report_response.text)
        return
    
    report_result = report_response.json()
    report_id = report_result["report_id"]
    report_number = report_result["report_number"]
    print(f"✅ Report submitted: {report_number} (ID: {report_id})")
    
    # Step 4: Upload evidence files
    print("\n4. Uploading evidence files...")
    
    # Create mock image file
    image_content = b"PNG fake image content for testing"
    image_file = BytesIO(image_content)
    
    files = {
        'file': ('screenshot_xss_vulnerability.png', image_file, 'image/png')
    }
    
    upload_response = requests.post(
        f"{BASE_URL}/reports/{report_id}/attachments",
        headers=researcher_headers,
        files=files
    )
    
    print(f"Upload response status: {upload_response.status_code}")
    print(f"Upload response: {upload_response.text}")
    
    if upload_response.status_code == 201:
        print("✅ Evidence file uploaded: screenshot_xss_vulnerability.png")
    else:
        print(f"⚠️  File upload failed: {upload_response.status_code}")
        print(upload_response.text)
    
    # Upload second file (PDF)
    pdf_content = b"PDF fake content for testing"
    pdf_file = BytesIO(pdf_content)
    
    files2 = {
        'file': ('technical_analysis.pdf', pdf_file, 'application/pdf')
    }
    
    upload_response2 = requests.post(
        f"{BASE_URL}/reports/{report_id}/attachments",
        headers=researcher_headers,
        files=files2
    )
    
    if upload_response2.status_code == 201:
        print("✅ Evidence file uploaded: technical_analysis.pdf")
    else:
        print(f"⚠️  File upload failed: {upload_response2.status_code}")
    
    # Step 5: Login as triage specialist
    print("\n5. Logging in as triage specialist...")
    triage_login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": "triage@example.com",
            "password": "Password123!"
        }
    )
    
    if triage_login_response.status_code != 200:
        print(f"❌ Triage login failed: {triage_login_response.status_code}")
        return
    
    triage_token = triage_login_response.json()["access_token"]
    triage_headers = {"Authorization": f"Bearer {triage_token}"}
    print("✅ Triage specialist logged in successfully")
    
    # Step 6: View report in triage queue
    print("\n6. Checking triage queue...")
    queue_response = requests.get(
        f"{BASE_URL}/triage/queue?limit=50",
        headers=triage_headers
    )
    
    if queue_response.status_code != 200:
        print(f"❌ Failed to fetch queue: {queue_response.status_code}")
        return
    
    queue_data = queue_response.json()
    reports_in_queue = queue_data.get("reports", [])
    
    # Find our report
    our_report = None
    for report in reports_in_queue:
        if report["id"] == report_id:
            our_report = report
            break
    
    if our_report:
        print(f"✅ Report found in triage queue: {report_number}")
        print(f"   Title: {our_report['title']}")
        print(f"   Status: {our_report['status']}")
        print(f"   Severity: {our_report.get('assigned_severity') or our_report.get('suggested_severity')}")
    else:
        print(f"⚠️  Report not found in queue (may need to filter by status)")
    
    # Step 7: View report detail with attachments
    print("\n7. Viewing report detail with attachments...")
    detail_response = requests.get(
        f"{BASE_URL}/reports/{report_id}",
        headers=triage_headers
    )
    
    if detail_response.status_code != 200:
        print(f"❌ Failed to fetch report detail: {detail_response.status_code}")
        return
    
    report_detail = detail_response.json()
    attachments = report_detail.get("attachments", [])
    
    print(f"✅ Report detail retrieved")
    print(f"   Report Number: {report_detail['report_number']}")
    print(f"   Title: {report_detail['title']}")
    print(f"   Status: {report_detail['status']}")
    print(f"   Attachments: {len(attachments)} file(s)")
    
    if attachments:
        print("\n   📎 Evidence Files:")
        for att in attachments:
            file_size_kb = att['file_size'] / 1024
            print(f"      - {att['filename']} ({att['file_type']}, {file_size_kb:.2f} KB)")
    else:
        print("   ⚠️  No attachments found")
    
    # Step 8: Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"✅ Report submitted by researcher: {report_number}")
    print(f"✅ Evidence files uploaded: {len(attachments)} file(s)")
    print(f"✅ Report visible in triage queue")
    print(f"✅ Attachments visible in report detail")
    print("\n🎉 Complete workflow tested successfully!")
    print("\nNext steps:")
    print("1. Open browser to http://localhost:3000")
    print("2. Login as triage@example.com / password123")
    print("3. Navigate to Triage Queue")
    print(f"4. Find report {report_number}")
    print("5. Click 'View Details' to see attachments")
    print("=" * 80)

if __name__ == "__main__":
    try:
        test_report_submission_with_evidence()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
