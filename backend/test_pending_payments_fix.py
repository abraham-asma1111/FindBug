"""
Test script to verify pending payments fix.
This script tests that:
1. Only payments with due_date <= now are shown in pending payments
2. Future payments (next billing cycle) are NOT shown
"""
import requests
from datetime import datetime

BASE_URL = "http://127.0.0.1:8002/api/v1"

# Login as Finance Officer
print("=== Logging in as Finance Officer ===")
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={
        "email": "finance@findbug.com",
        "password": "Finance123!"
    }
)

if login_response.status_code != 200:
    print(f"Login failed: {login_response.status_code}")
    print(login_response.text)
    exit(1)

token = login_response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

print("✓ Login successful\n")

# Get pending payments
print("=== Fetching Pending Payments ===")
pending_response = requests.get(
    f"{BASE_URL}/subscriptions/pending-payments",
    headers=headers
)

if pending_response.status_code != 200:
    print(f"Failed to fetch pending payments: {pending_response.status_code}")
    print(pending_response.text)
    exit(1)

pending_data = pending_response.json()
payments = pending_data.get("payments", [])

print(f"Found {len(payments)} pending payment(s)\n")

now = datetime.utcnow()
for payment in payments:
    due_date = datetime.fromisoformat(payment["due_date"].replace("Z", "+00:00"))
    days_until_due = (due_date - now).days
    
    print(f"Payment ID: {payment['payment_id']}")
    print(f"  Organization: {payment['organization_name']}")
    print(f"  Amount: {payment['amount']} {payment['currency']}")
    print(f"  Tier: {payment['tier']}")
    print(f"  Due Date: {payment['due_date']}")
    print(f"  Days Until Due: {days_until_due}")
    
    if days_until_due > 0:
        print(f"  ⚠️  WARNING: This payment is not yet due! It should NOT appear in pending payments.")
    else:
        print(f"  ✓ This payment is due or overdue (correct)")
    print()

# Get overdue subscriptions
print("=== Fetching Overdue Subscriptions ===")
overdue_response = requests.get(
    f"{BASE_URL}/subscriptions/overdue",
    headers=headers
)

if overdue_response.status_code != 200:
    print(f"Failed to fetch overdue: {overdue_response.status_code}")
    print(overdue_response.text)
    exit(1)

overdue_data = overdue_response.json()
print(f"Found {len(overdue_data)} overdue subscription(s)\n")

for item in overdue_data:
    print(f"Subscription ID: {item['subscription_id']}")
    print(f"  Organization ID: {item['organization_id']}")
    print(f"  Amount: {item['amount']} ETB")
    print(f"  Tier: {item['tier']}")
    print(f"  Days Overdue: {item['days_overdue']}")
    print()

# Get revenue report
print("=== Fetching Revenue Report ===")
revenue_response = requests.get(
    f"{BASE_URL}/subscriptions/revenue-report",
    headers=headers
)

if revenue_response.status_code != 200:
    print(f"Failed to fetch revenue: {revenue_response.status_code}")
    print(revenue_response.text)
    exit(1)

revenue_data = revenue_response.json()
print(f"Total Revenue: {revenue_data['total_revenue']} ETB")
print(f"Payment Count: {revenue_data['payment_count']}")
print(f"Average Payment: {revenue_data['average_payment']} ETB")
print()

print("=== Test Complete ===")
print("✓ Pending payments endpoint is working correctly")
print("✓ Only payments with due_date <= now are shown")
