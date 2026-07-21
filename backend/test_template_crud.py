#!/usr/bin/env python3
"""Test template CRUD operations."""
import requests
import json

BASE_URL = "http://127.0.0.1:8002/api/v1"

# Login as triage specialist
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={"email": "triage@bugbounty.com", "password": "triage123"}
)
print(f"Login: {login_response.status_code}")
token = login_response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# List templates
print("\n1. LIST templates:")
list_response = requests.get(f"{BASE_URL}/triage/templates", headers=headers)
print(f"Status: {list_response.status_code}")
templates = list_response.json()["templates"]
print(f"Found {len(templates)} templates")
for t in templates[:3]:
    print(f"  - {t['name']}: {t['title']}")

# Create template with unique name
print("\n2. CREATE template:")
create_data = {
    "name": f"test_template_{len(templates)+1}",
    "title": "Test Template",
    "content": "This is a test template content",
    "category": "validation"
}
create_response = requests.post(
    f"{BASE_URL}/triage/templates",
    headers=headers,
    json=create_data
)
print(f"Status: {create_response.status_code}")
if create_response.status_code == 201:
    new_template = create_response.json()["template"]
    template_id = new_template["id"]
    print(f"Created template ID: {template_id}")
    
    # Update template
    print("\n3. UPDATE template:")
    update_data = {
        "name": create_data["name"],
        "title": "Updated Test Template",
        "content": "Updated content",
        "category": "rejection",
        "is_active": True
    }
    update_response = requests.put(
        f"{BASE_URL}/triage/templates/{template_id}",
        headers=headers,
        json=update_data
    )
    print(f"Status: {update_response.status_code}")
    if update_response.status_code == 200:
        print("Template updated successfully")
    else:
        print(f"Error: {update_response.text}")
    
    # Delete template
    print("\n4. DELETE template:")
    delete_response = requests.delete(
        f"{BASE_URL}/triage/templates/{template_id}",
        headers=headers
    )
    print(f"Status: {delete_response.status_code}")
    if delete_response.status_code == 200:
        print("Template deleted successfully")
    else:
        print(f"Error: {delete_response.text}")
else:
    print(f"Error creating: {create_response.text}")
