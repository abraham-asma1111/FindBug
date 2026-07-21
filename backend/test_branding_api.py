"""Test branding API response."""
import requests

# Test Company ID
org_id = "7c3b13e0-afb3-460b-b240-a74eb83e574c"

# You need to login as finance officer first to get the token
# For now, let's just test without auth to see the structure

url = f"http://localhost:8002/api/v1/financial/organizations/{org_id}"

try:
    # This will fail with 401, but let's see the endpoint structure
    response = requests.get(url)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("\nResponse Data:")
        print(f"Company: {data.get('company_name')}")
        print(f"Branding: {data.get('branding')}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Error: {e}")

print("\n--- Testing with finance officer token ---")
print("Please login as finance officer and get the token from browser DevTools")
print("Then run: curl -H 'Authorization: Bearer YOUR_TOKEN' http://localhost:8002/api/v1/financial/organizations/7c3b13e0-afb3-460b-b240-a74eb83e574c")
