"""
Test the /payment-methods/all endpoint
"""
import requests

BASE_URL = "http://localhost:8000/api/v1"

# You'll need to get a valid token first
# For now, let's just test if the endpoint is accessible
response = requests.get(f"{BASE_URL}/payment-methods/all")

print("=" * 80)
print("Testing /payment-methods/all endpoint")
print("=" * 80)
print(f"\nStatus Code: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    print(f"\nTotal payment methods returned: {len(data)}")
    
    pending_count = sum(1 for pm in data if not pm.get('is_verified'))
    approved_count = sum(1 for pm in data if pm.get('is_verified'))
    
    print(f"  - Pending: {pending_count}")
    print(f"  - Approved: {approved_count}")
    
    print("\nPayment Methods:")
    for pm in data:
        status = "APPROVED" if pm.get('is_verified') else "PENDING"
        researcher = pm.get('researcher', {})
        print(f"  - {researcher.get('email', 'Unknown')}: {pm.get('method_type')} - {status}")
else:
    print(f"\nError: {response.text}")

print("\n" + "=" * 80)
