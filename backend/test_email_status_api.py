#!/usr/bin/env python3
"""Test email status API endpoint"""
import sys
import requests

# Login first
login_response = requests.post(
    "http://localhost:8002/api/v1/auth/login",
    json={
        "email": "abrahambecon@gmail.com",
        "password": "Test123!@#"
    }
)

if login_response.status_code != 200:
    print(f"❌ Login failed: {login_response.status_code}")
    print(login_response.text)
    sys.exit(1)

token = login_response.json()["access_token"]
print(f"✅ Login successful, got token")

# Check email status
status_response = requests.get(
    "http://localhost:8002/api/v1/kyc/email/status",
    headers={"Authorization": f"Bearer {token}"}
)

print(f"\n📋 Email Status API Response (status code: {status_response.status_code}):")
print(status_response.json())

# Also check persona status for comparison
persona_response = requests.get(
    "http://localhost:8002/api/v1/kyc/persona/status",
    headers={"Authorization": f"Bearer {token}"}
)

print(f"\n📋 Persona Status API Response (status code: {persona_response.status_code}):")
print(persona_response.json())
