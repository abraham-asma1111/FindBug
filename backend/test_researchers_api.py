import requests
import json

# Login with researcher account
login_response = requests.post(
    "http://localhost:8002/api/v1/auth/login",
    json={"email": "researcher@test.com", "password": "password123"}
)
print("Login response:", login_response.json())

if "access_token" not in login_response.json():
    print("Login failed, trying with staff account...")
    login_response = requests.post(
        "http://localhost:8002/api/v1/auth/login",
        json={"email": "staff@example.com", "password": "password123"}
    )
    print("Staff login response:", login_response.json())

token = login_response.json()["access_token"]

# Get researchers list
headers = {"Authorization": f"Bearer {token}"}
response = requests.get("http://localhost:8002/api/v1/triage/researchers", headers=headers)

print("Status Code:", response.status_code)
print("\nResponse:")
data = response.json()
print(json.dumps(data, indent=2))

# Check spam scores
if "researchers" in data:
    print("\n=== SPAM SCORES ===")
    for r in data["researchers"]:
        print(f"{r['username']}: spam_score = {r['spam_score']} (type: {type(r['spam_score'])})")
