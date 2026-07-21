"""Test admin users endpoint."""
import requests
import json

# Login as admin
login_response = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    json={
        "email": "remainsecure@findbug.com",
        "password": "admin123"
    }
)

if login_response.status_code != 200:
    print(f"Login failed: {login_response.status_code}")
    print(login_response.text)
    exit(1)

token = login_response.json()["access_token"]
print(f"✓ Logged in successfully")

# Test users endpoint
headers = {"Authorization": f"Bearer {token}"}

print("\n1. Testing /admin/users (no filters):")
response = requests.get("http://localhost:8000/api/v1/admin/users", headers=headers)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"Total users: {data.get('total', 0)}")
    print(f"Users returned: {len(data.get('users', []))}")
    if data.get('users'):
        print(f"\nFirst user sample:")
        print(json.dumps(data['users'][0], indent=2, default=str))
else:
    print(f"Error: {response.text}")

print("\n2. Testing /admin/users?role=researcher:")
response = requests.get("http://localhost:8000/api/v1/admin/users?role=researcher", headers=headers)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"Researchers: {len(data.get('users', []))}")
else:
    print(f"Error: {response.text}")

print("\n3. Testing /admin/users?search=test:")
response = requests.get("http://localhost:8000/api/v1/admin/users?search=test", headers=headers)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"Search results: {len(data.get('users', []))}")
else:
    print(f"Error: {response.text}")
