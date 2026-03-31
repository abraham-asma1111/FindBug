"""Debug registration endpoint"""
import sys
sys.path.insert(0, ".")

from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

# Test researcher registration
register_data = {
    "email": "testresearcher@test.com",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!",
    "first_name": "Test",
    "last_name": "Researcher"
}

print("Testing researcher registration...")
print(f"Data: {register_data}")

response = client.post("/api/v1/auth/register/researcher", json=register_data)

print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
