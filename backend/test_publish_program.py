#!/usr/bin/env python3
"""Test script to verify publish program endpoint"""
import requests
import json

BASE_URL = "http://127.0.0.1:8002/api/v1"

# Login as organization
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={
        "email": "org@example.com",
        "password": "password123"
    }
)

print("Login Response:", login_response.status_code)
print(json.dumps(login_response.json(), indent=2))

if login_response.status_code != 200:
    print("Login failed!")
    exit(1)

token = login_response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Get programs
programs_response = requests.get(f"{BASE_URL}/programs", headers=headers)
print("\nPrograms Response:", programs_response.status_code)
programs = programs_response.json()
print(f"Found {len(programs)} programs")

# Find a draft program
draft_program = None
for program in programs:
    if program["status"] == "draft":
        draft_program = program
        break

if not draft_program:
    print("\nNo draft program found. Creating one...")
    create_response = requests.post(
        f"{BASE_URL}/programs",
        headers=headers,
        json={
            "name": "Test Publish Program",
            "description": "Testing publish functionality",
            "type": "bounty"
        }
    )
    print("Create Response:", create_response.status_code)
    if create_response.status_code == 201:
        draft_program = create_response.json()
        print(f"Created program: {draft_program['id']}")
    else:
        print("Failed to create program:", create_response.text)
        exit(1)

print(f"\nTesting publish for program: {draft_program['id']}")
print(f"Program name: {draft_program['name']}")
print(f"Program status: {draft_program['status']}")

# Try to publish
publish_response = requests.post(
    f"{BASE_URL}/programs/{draft_program['id']}/publish",
    headers=headers
)

print(f"\nPublish Response: {publish_response.status_code}")
print(json.dumps(publish_response.json(), indent=2))
