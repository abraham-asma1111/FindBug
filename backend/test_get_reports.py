#!/usr/bin/env python3
"""Test getting researcher reports."""
import requests
import json

BASE_URL = "http://localhost:8002/api/v1"

def test_get_reports():
    print("Testing Get Researcher Reports")
    print("=" * 60)
    
    # Login as researcher
    print("\n1. Logging in as researcher...")
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": "researcher@test.com",
            "password": "Password123!"
        }
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(login_response.text)
        return
    
    token = login_response.json()["access_token"]
    print("✓ Logged in")
    
    # Get reports
    print("\n2. Fetching reports...")
    headers = {"Authorization": f"Bearer {token}"}
    reports_response = requests.get(
        f"{BASE_URL}/reports/my-reports",
        headers=headers
    )
    
    print(f"\nStatus: {reports_response.status_code}")
    
    if reports_response.status_code == 200:
        reports = reports_response.json()
        print(f"\nFound {len(reports)} reports")
        print(json.dumps(reports, indent=2))
    else:
        print(f"❌ Failed to get reports")
        print(reports_response.text)

if __name__ == "__main__":
    test_get_reports()
