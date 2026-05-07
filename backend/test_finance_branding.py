"""Test finance organization endpoint with branding data."""
import requests
import json

BASE_URL = "http://localhost:8002/api/v1"

# Finance officer credentials
FINANCE_EMAIL = "finance@findbug.com"
FINANCE_PASSWORD = "password123"  # Replace with actual password

def test_finance_organization_branding():
    """Test that finance organization endpoint returns branding data."""
    
    print("=" * 60)
    print("Testing Finance Organization Endpoint - Branding Data")
    print("=" * 60)
    
    # 1. Login as finance officer
    print("\n1. Logging in as finance officer...")
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": FINANCE_EMAIL,
            "password": FINANCE_PASSWORD
        }
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(f"Response: {login_response.text}")
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Login successful")
    
    # 2. Get organizations list
    print("\n2. Getting organizations list...")
    orgs_response = requests.get(
        f"{BASE_URL}/financial/organizations",
        headers=headers
    )
    
    if orgs_response.status_code != 200:
        print(f"❌ Failed to get organizations: {orgs_response.status_code}")
        print(f"Response: {orgs_response.text}")
        return
    
    orgs_data = orgs_response.json()
    print(f"✅ Retrieved {len(orgs_data.get('organizations', []))} organizations")
    
    if not orgs_data.get('organizations'):
        print("⚠️  No organizations found in database")
        return
    
    # 3. Get first organization details with branding
    org_id = orgs_data['organizations'][0]['id']
    print(f"\n3. Getting organization details for ID: {org_id}...")
    
    org_detail_response = requests.get(
        f"{BASE_URL}/financial/organizations/{org_id}",
        headers=headers
    )
    
    if org_detail_response.status_code != 200:
        print(f"❌ Failed to get organization details: {org_detail_response.status_code}")
        print(f"Response: {org_detail_response.text}")
        return
    
    org_detail = org_detail_response.json()
    print("✅ Organization details retrieved successfully")
    
    # 4. Check branding data
    print("\n4. Checking branding data...")
    if 'branding' in org_detail:
        print("✅ Branding data present in response")
        print(f"\nBranding details:")
        print(f"  - Logo URL: {org_detail['branding'].get('logo_url', 'Not set')}")
        print(f"  - Cover Image URL: {org_detail['branding'].get('cover_image_url', 'Not set')}")
        print(f"  - Brand Color: {org_detail['branding'].get('brand_color', 'Not set')}")
        print(f"  - Theme Settings: {org_detail['branding'].get('theme_settings', 'Not set')}")
    else:
        print("❌ Branding data missing from response")
    
    print("\n" + "=" * 60)
    print("Finance Organization Branding Test Complete")
    print("=" * 60)


if __name__ == "__main__":
    test_finance_organization_branding()
