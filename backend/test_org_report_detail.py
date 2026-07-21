"""
Test organization report detail access fix
"""
import requests

BASE_URL = "http://localhost:8002/api/v1"

# Login as organization
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={
        "email": "org@test.com",
        "password": "Password123!"
    }
)

if login_response.status_code == 200:
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get reports list
    reports_response = requests.get(
        f"{BASE_URL}/reports",
        headers=headers
    )
    
    print(f"Reports list status: {reports_response.status_code}")
    
    if reports_response.status_code == 200:
        reports_data = reports_response.json()
        reports = reports_data.get("reports", [])
        
        print(f"Found {len(reports)} reports")
        
        if reports:
            # Try to access first report detail
            report_id = reports[0]["id"]
            print(f"\nTrying to access report: {report_id}")
            
            detail_response = requests.get(
                f"{BASE_URL}/reports/{report_id}",
                headers=headers
            )
            
            print(f"Report detail status: {detail_response.status_code}")
            
            if detail_response.status_code == 200:
                print("✅ SUCCESS! Organization can now view their report details")
                report = detail_response.json()
                print(f"Report title: {report.get('title')}")
                print(f"Report status: {report.get('status')}")
            else:
                print(f"❌ FAILED: {detail_response.text}")
        else:
            print("No reports found to test")
    else:
        print(f"Failed to get reports: {reports_response.text}")
else:
    print(f"Login failed: {login_response.text}")
