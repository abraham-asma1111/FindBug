"""
Test script to verify wallet deduction fix for subscription payments.
"""
import requests
import psycopg2
from psycopg2.extras import RealDictCursor

BASE_URL = "http://127.0.0.1:8002/api/v1"

# Get initial wallet balance from database
def get_wallet_balance():
    conn = psycopg2.connect(
        dbname="bug_bounty_production",
        user="bugbounty_user",
        password="changeme123",
        host="localhost",
        port="5432"
    )
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Get organization's user_id
    cur.execute("""
        SELECT user_id FROM organizations 
        WHERE id = '7c3b13e0-afb3-460b-b240-a74eb83e574c'
    """)
    org = cur.fetchone()
    user_id = org['user_id']
    
    # Get wallet balance
    cur.execute("""
        SELECT balance, available_balance 
        FROM wallets 
        WHERE owner_id = %s AND owner_type = 'organization'
    """, (user_id,))
    
    wallet = cur.fetchone()
    cur.close()
    conn.close()
    
    return wallet

print("=" * 60)
print("TEST: Wallet Deduction for Subscription Payment")
print("=" * 60)

# Get initial balance
print("\n1. Checking initial wallet balance...")
initial_wallet = get_wallet_balance()
print(f"✓ Initial Balance: {initial_wallet['balance']} ETB")
print(f"✓ Available Balance: {initial_wallet['available_balance']} ETB")

# Login as Organization
print("\n2. Logging in as Organization...")
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={
        "email": "org@test.com",
        "password": "Password123!"
    }
)

if login_response.status_code != 200:
    print(f"❌ Login failed: {login_response.status_code}")
    print(login_response.text)
    exit(1)

token = login_response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print("✓ Login successful")

# Cancel existing subscription if any
print("\n3. Checking for existing subscription...")
sub_response = requests.get(
    f"{BASE_URL}/subscriptions/current",
    headers=headers
)

if sub_response.status_code == 200:
    subscription = sub_response.json()
    print(f"✓ Found existing subscription: {subscription['subscription_id']}")
    print(f"  Cancelling subscription...")
    
    cancel_response = requests.post(
        f"{BASE_URL}/subscriptions/{subscription['subscription_id']}/cancel",
        headers=headers,
        json={"reason": "Testing wallet deduction"}
    )
    
    if cancel_response.status_code == 200:
        print("✓ Subscription cancelled")
    else:
        print(f"⚠️  Failed to cancel: {cancel_response.status_code}")
else:
    print("✓ No existing subscription")

# Create new subscription with wallet payment
print("\n4. Creating new subscription with wallet payment...")
print("  Tier: BASIC (15,000 ETB)")
print("  Payment Method: Pay from Wallet")

create_response = requests.post(
    f"{BASE_URL}/subscriptions",
    headers=headers,
    json={
        "organization_id": "7c3b13e0-afb3-460b-b240-a74eb83e574c",
        "tier": "BASIC",
        "trial_days": 0,
        "pay_from_wallet": True
    }
)

if create_response.status_code != 201:
    print(f"❌ Subscription creation failed: {create_response.status_code}")
    print(create_response.text)
    exit(1)

subscription = create_response.json()
print(f"✓ Subscription created: {subscription['subscription_id']}")
print(f"  Tier: {subscription['tier']}")
print(f"  Status: {subscription['status']}")
print(f"  Fee: {subscription['subscription_fee']} {subscription['currency']}")

# Get final wallet balance
print("\n5. Checking final wallet balance...")
final_wallet = get_wallet_balance()
print(f"✓ Final Balance: {final_wallet['balance']} ETB")
print(f"✓ Available Balance: {final_wallet['available_balance']} ETB")

# Calculate deduction
deducted = float(initial_wallet['balance']) - float(final_wallet['balance'])
expected_deduction = 15000.00  # BASIC tier price

print("\n" + "=" * 60)
print("RESULTS")
print("=" * 60)
print(f"Initial Balance: {initial_wallet['balance']} ETB")
print(f"Final Balance: {final_wallet['balance']} ETB")
print(f"Amount Deducted: {deducted} ETB")
print(f"Expected Deduction: {expected_deduction} ETB")

if abs(deducted - expected_deduction) < 0.01:
    print("\n✅ SUCCESS: Wallet was correctly deducted!")
else:
    print(f"\n❌ FAIL: Wallet deduction incorrect!")
    print(f"   Expected: {expected_deduction} ETB")
    print(f"   Actual: {deducted} ETB")
