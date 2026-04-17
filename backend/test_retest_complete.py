#!/usr/bin/env python3
"""
Test script to debug retest completion 422 error
"""
import requests
import json

# Test data
retest_id = "9edf8d63-fc5f-4565-a45e-ebaf79a8bf9b"
api_url = "http://localhost:8002"

# Get researcher token (you'll need to update this with actual token)
# For now, let's just test the endpoint structure

# Test payload
payload = {
    "retest_result": "FIXED",
    "retest_notes": "The vulnerability has been completely fixed. I verified the fix by attempting the same exploit and it no longer works.",
    "retest_evidence": ["https://example.com/evidence1.png"]
}

print("Testing retest completion endpoint...")
print(f"URL: {api_url}/api/v1/ptaas/retests/{retest_id}/complete")
print(f"Payload: {json.dumps(payload, indent=2)}")

# Make request (will fail without auth, but we can see the error)
try:
    response = requests.post(
        f"{api_url}/api/v1/ptaas/retests/{retest_id}/complete",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
