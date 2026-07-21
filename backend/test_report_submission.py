#!/usr/bin/env python3
"""Test report submission."""

import requests
import json

API_URL = "http://127.0.0.1:8002/api/v1"

def login(email, password):
    """Login and get access token."""
    response = requests.post(
        f"{API_URL}/auth/login",
        json={"email": email, "password": password}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    return None

def submit_report(token, program_id):
    """Submit a test report."""
    headers = {"Authorization": f"Bearer {token}"}
    
    report_data = {
        "program_id": program_id,
        "title": "Test SQL Injection Vulnerability",
        "description": "This is a test description that is longer than 50 characters to meet the minimum requirement for report submission.",
        "suggested_severity": "high",
        "vulnerability_type": "SQL Injection",
        "steps_to_reproduce": "1. Navigate to login page\n2. Enter ' OR '1'='1 in username\n3. Click submit\n4. Observe SQL error",
        "impact_assessment": "An attacker could bypass authentication and gain unauthorized access to user accounts.",
        "affected_asset": "https://example.com/login"
    }
    
    print("\n=== Submitting Report ===")
    print(f"Data: {json.dumps(report_data, indent=2)}")
    
    response = requests.post(
        f"{API_URL}/reports",
        headers=headers,
        json=report_data
    )
    
    print(f"\nStatus: {response.status_code}")
    print(f"Response: {response.text}")
    
    return response

def main():
    print("Testing Report Submission")
    print("=" * 60)
    
    # Login
    print("\n1. Logging in as researcher...")
    token = login("researcher@test.com", "Password123!")
    if not token:
        print("❌ Login failed")
        return
    print("✓ Logged in")
    
    # Submit report
    program_id = "ade9b88b-d3e2-444b-9546-fdf9eac0a273"
    response = submit_report(token, program_id)
    
    if response.status_code == 201:
        print("\n✓ Report submitted successfully!")
    elif response.status_code == 500:
        print("\n❌ 500 Internal Server Error")
        print("Check backend terminal for Python traceback")
    else:
        print(f"\n❌ Failed with status {response.status_code}")

if __name__ == "__main__":
    main()
