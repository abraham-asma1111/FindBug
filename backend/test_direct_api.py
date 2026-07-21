#!/usr/bin/env python3
"""
Direct API test to see validation errors
"""
import requests
import sys

# Get auth token first
login_response = requests.post(
    "http://localhost:8002/api/v1/auth/login",
    json={
        "email": "researcher@test.com",
        "password": "Test123!@#"
    }
)

if login_response.status_code != 200:
    print(f"Login failed: {login_response.status_code}")
    print(login_response.text)
    sys.exit(1)

token = login_response.json()["access_token"]
print(f"Got token: {token[:20]}...")

# Now test the retest completion
retest_id = "9edf8d63-fc5f-4565-a45e-ebaf79a8bf9b"
payload = {
    "retest_result": "FIXED",
    "retest_notes": "The vulnerability has been completely fixed and verified.",
    "retest_evidence": ["https://example.com/evidence1.png"]
}

print(f"\nTesting POST /api/v1/ptaas/retests/{retest_id}/complete")
print(f"Payload: {payload}")

response = requests.post(
    f"http://localhost:8002/api/v1/ptaas/retests/{retest_id}/complete",
    json=payload,
    headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
)

print(f"\nStatus: {response.status_code}")
print(f"Response: {response.text}")

if response.status_code == 422:
    import json
    try:
        error_detail = json.loads(response.text)
        print("\nValidation Error Details:")
        print(json.dumps(error_detail, indent=2))
    except:
        pass
