"""Test organization branding endpoints."""
import requests
import json

BASE_URL = "http://localhost:8002/api/v1"

# Test with organization user credentials
# You'll need to replace these with actual organization credentials
ORG_EMAIL = "org@example.com"  # Replace with actual org email
ORG_PASSWORD = "password123"  # Replace with actual org password

def test_branding_endpoints():
    """Test all branding endpoints."""
    
    print("=" * 60)
    print("Testing Organization Branding Endpoints")
    print("=" * 60)
    
    # 1. Login as organization
    print("\n1. Logging in as organization...")
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": ORG_EMAIL,
            "password": ORG_PASSWORD
        }
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(f"Response: {login_response.text}")
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Login successful")
    
    # 2. Get current branding
    print("\n2. Getting current branding settings...")
    branding_response = requests.get(
        f"{BASE_URL}/organization/branding/",
        headers=headers
    )
    
    if branding_response.status_code == 200:
        print("✅ Branding retrieved successfully")
        print(f"Current branding: {json.dumps(branding_response.json(), indent=2)}")
    else:
        print(f"❌ Failed to get branding: {branding_response.status_code}")
        print(f"Response: {branding_response.text}")
    
    # 3. Update brand color
    print("\n3. Updating brand color...")
    update_response = requests.put(
        f"{BASE_URL}/organization/branding/settings",
        headers=headers,
        json={
            "brand_color": "#10B981"
        }
    )
    
    if update_response.status_code == 200:
        print("✅ Brand color updated successfully")
        print(f"Response: {json.dumps(update_response.json(), indent=2)}")
    else:
        print(f"❌ Failed to update brand color: {update_response.status_code}")
        print(f"Response: {update_response.text}")
    
    # 4. Verify update
    print("\n4. Verifying brand color update...")
    verify_response = requests.get(
        f"{BASE_URL}/organization/branding/",
        headers=headers
    )
    
    if verify_response.status_code == 200:
        branding_data = verify_response.json()
        if branding_data.get("brand_color") == "#10B981":
            print("✅ Brand color verified successfully")
        else:
            print(f"⚠️  Brand color mismatch: {branding_data.get('brand_color')}")
    
    print("\n" + "=" * 60)
    print("Branding Endpoints Test Complete")
    print("=" * 60)
    print("\nNote: File upload tests require actual image files.")
    print("You can test logo/cover uploads through the frontend UI.")


if __name__ == "__main__":
    test_branding_endpoints()
