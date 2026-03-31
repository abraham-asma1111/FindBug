"""Debug token issue"""
import sys
sys.path.insert(0, ".")

from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

# Register and login
register_response = client.post("/api/v1/auth/register/researcher", json={
    "email": "tokentest@test.com",
    "password": "Test123!@#",
    "password_confirm": "Test123!@#",
    "first_name": "Token",
    "last_name": "Test"
})

print(f"Register status: {register_response.status_code}")

login_response = client.post("/api/v1/auth/login", json={
    "email": "tokentest@test.com",
    "password": "Test123!@#"
})

print(f"Login status: {login_response.status_code}")
if login_response.status_code == 200:
    token = login_response.json()["access_token"]
    print(f"Token: {token[:50]}...")
    
    # Try to access profile
    headers = {"Authorization": f"Bearer {token}"}
    profile_response = client.get("/api/v1/profile", headers=headers)
    print(f"Profile status: {profile_response.status_code}")
    if profile_response.status_code == 200:
        print(f"Profile data: {profile_response.json()}")
    else:
        print(f"Profile error: {profile_response.json()}")
