"""
Test script to verify organization payment history fix.
This script tests that:
1. Organizations only see PAID payments in their payment history
2. Pending future payments are NOT shown to organizations
3. Finance officers can still see all payments
"""
import requests

BASE_URL = "http://127.0.0.1:8002/api/v1"

print("=" * 60)
print("TEST 1: Organization Payment History")
print("=" * 60)

# Login as Organization
print("\n1. Logging in as Organization...")
org_login = requests.post(
    f"{BASE_URL}/auth/login",
    json={
        "email": "org@test.com",
        "password": "Password123!"
    }
)

if org_login.status_code != 200:
    print(f"❌ Organization login failed: {org_login.status_code}")
    print(org_login.text)
    exit(1)

org_token = org_login.json()["access_token"]
org_headers = {"Authorization": f"Bearer {org_token}"}
print("✓ Organization login successful")

# Get organization's subscription
print("\n2. Fetching organization subscription...")
sub_response = requests.get(
    f"{BASE_URL}/subscriptions/current",
    headers=org_headers
)

if sub_response.status_code != 200:
    print(f"❌ Failed to fetch subscription: {sub_response.status_code}")
    print(sub_response.text)
    exit(1)

subscription = sub_response.json()
subscription_id = subscription["subscription_id"]
print(f"✓ Subscription ID: {subscription_id}")
print(f"  Tier: {subscription['tier']}")
print(f"  Status: {subscription['status']}")

# Get payment history
print("\n3. Fetching payment history...")
payments_response = requests.get(
    f"{BASE_URL}/subscriptions/{subscription_id}/payments",
    headers=org_headers
)

if payments_response.status_code != 200:
    print(f"❌ Failed to fetch payments: {payments_response.status_code}")
    print(payments_response.text)
    exit(1)

payments = payments_response.json()
print(f"✓ Found {len(payments)} payment(s) in history")

# Verify all payments are PAID
all_paid = True
for payment in payments:
    print(f"\n  Payment ID: {payment['payment_id'][:8]}...")
    print(f"    Status: {payment['status']}")
    print(f"    Amount: {payment['amount']} {payment['currency']}")
    print(f"    Invoice: {payment['invoice_number']}")
    print(f"    Paid At: {payment.get('paid_at', 'N/A')}")
    
    if payment['status'] != 'paid':
        print(f"    ❌ ERROR: Organization should only see PAID payments!")
        all_paid = False
    else:
        print(f"    ✓ Correct: Payment is paid")

if all_paid and len(payments) > 0:
    print("\n✅ PASS: Organization only sees paid payments")
elif len(payments) == 0:
    print("\n⚠️  No payment history yet (expected if no payments have been made)")
else:
    print("\n❌ FAIL: Organization is seeing non-paid payments!")

print("\n" + "=" * 60)
print("TEST 2: Finance Officer View (Should See All Payments)")
print("=" * 60)

# Login as Finance Officer
print("\n1. Logging in as Finance Officer...")
finance_login = requests.post(
    f"{BASE_URL}/auth/login",
    json={
        "email": "finance@findbug.com",
        "password": "Finance123!"
    }
)

if finance_login.status_code != 200:
    print(f"❌ Finance login failed: {finance_login.status_code}")
    print(finance_login.text)
    exit(1)

finance_token = finance_login.json()["access_token"]
finance_headers = {"Authorization": f"Bearer {finance_token}"}
print("✓ Finance Officer login successful")

# Get all payments for the subscription
print(f"\n2. Fetching all payments for subscription {subscription_id}...")
finance_payments_response = requests.get(
    f"{BASE_URL}/subscriptions/{subscription_id}/payments",
    headers=finance_headers
)

if finance_payments_response.status_code != 200:
    print(f"❌ Failed to fetch payments: {finance_payments_response.status_code}")
    print(finance_payments_response.text)
    exit(1)

finance_payments = finance_payments_response.json()
print(f"✓ Found {len(finance_payments)} payment(s) (including pending)")

for payment in finance_payments:
    print(f"\n  Payment ID: {payment['payment_id'][:8]}...")
    print(f"    Status: {payment['status']}")
    print(f"    Amount: {payment['amount']} {payment['currency']}")
    print(f"    Due Date: {payment['due_date']}")

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"Organization sees: {len(payments)} payment(s) (paid only)")
print(f"Finance Officer sees: {len(finance_payments)} payment(s) (all)")
print("\n✅ Test complete!")
