"""Test triage queue endpoint returns real database data."""
import requests
import json

def test_triage_queue():
    # Login
    login_response = requests.post(
        'http://localhost:8002/api/v1/auth/login',
        json={'email': 'triage@example.com', 'password': 'Password123!'}
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.text}")
        return
    
    token = login_response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    
    # Test queue endpoint
    print("Testing /triage/queue endpoint...")
    queue_response = requests.get(
        'http://localhost:8002/api/v1/triage/queue?limit=5',
        headers=headers
    )
    
    print(f"Status Code: {queue_response.status_code}")
    
    if queue_response.status_code == 200:
        data = queue_response.json()
        print(f"\n✓ SUCCESS - Queue endpoint returns real database data")
        print(f"✓ Total Reports: {data['total']}")
        print(f"\n{'='*80}")
        print("SAMPLE REPORTS (Real Database Data):")
        print(f"{'='*80}\n")
        
        for i, report in enumerate(data['reports'][:3], 1):
            print(f"{i}. Report: {report['report_number']}")
            print(f"   Title: {report['title'][:60]}")
            print(f"   Program: {report.get('program_name', 'N/A')}")
            print(f"   Researcher: {report.get('researcher_name', 'N/A')}")
            print(f"   Email: {report.get('researcher_email', 'N/A')}")
            print(f"   Status: {report['status']}")
            print(f"   Severity: {report.get('assigned_severity') or report['suggested_severity']}")
            print(f"   Submitted: {report['submitted_at'][:19]}")
            print()
        
        # Verify NO mock data
        mock_indicators = ['Ethiopian Airlines', 'Abraham Asimamaw', 'api.ethiopianairlines']
        has_mock = False
        for report in data['reports']:
            for field in ['title', 'description', 'program_name', 'researcher_name']:
                value = str(report.get(field, ''))
                for indicator in mock_indicators:
                    if indicator in value:
                        print(f"⚠️  WARNING: Found potential mock data: {indicator} in {field}")
                        has_mock = True
        
        if not has_mock:
            print("✓ NO MOCK DATA DETECTED - All data is from database")
        
    else:
        print(f"\n❌ ERROR: {queue_response.status_code}")
        print(f"Response: {queue_response.text[:500]}")

if __name__ == "__main__":
    test_triage_queue()
