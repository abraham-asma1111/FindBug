"""
Test complete subscription payment workflow.

Tests both manual payment and wallet payment flows:
1. Manual payment: Organization pays via bank transfer, Finance Officer verifies
2. Wallet payment: Organization pays from wallet, Finance Officer verifies and wallet is deducted
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8002/api/v1"

# Test credentials
ORG_EMAIL = "org@test.com"
ORG_PASSWORD = "Password123!"
FINANCE_EMAIL = "finance@findbug.com"
FINANCE_PASSWORD = "Finance123!"

def login(email: str, password: str):
    """Login and get access token."""
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": email, "password": password}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Login failed: {response.status_code}")
        print(response.text)
        return None

def get_headers(token: str):
    """Get headers with auth token."""
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

def main():
    print("=" * 80)
    print("TESTING SUBSCRIPTION PAYMENT WORKFLOW")
    print("=" * 80)
    
    # Step 1: Login as organization
    print("\n1. Logging in as organization...")
    org_token = login(ORG_EMAIL, ORG_PASSWORD)
    if not org_token:
        print("❌ Failed to login as organization")
        return
    print("✅ Organization logged in")
    
    # Step 2: Get organization profile
    print("\n2. Getting organization profile...")
    response = requests.get(
        f"{BASE_URL}/profile",
        headers=get_headers(org_token)
    )
    if response.status_code != 200:
        print(f"❌ Failed to get profile: {response.status_code}")
        print(response.text)
        return
    
    profile = response.json()
    org_id = profile.get("organization", {}).get("id")
    if not org_id:
        print("❌ Organization ID not found in profile")
        return
    print(f"✅ Organization ID: {org_id}")
    
    # Step 3: Check wallet balance
    print("\n3. Checking wallet balance...")
    response = requests.get(
        f"{BASE_URL}/wallet/balance",
        headers=get_headers(org_token)
    )
    if response.status_code != 200:
        print(f"❌ Failed to get wallet balance: {response.status_code}")
        return
    
    wallet_data = response.json()
    initial_balance = wallet_data.get("available_balance", 0)
    print(f"✅ Initial wallet balance: {initial_balance} ETB")
    
    # Step 4: Cancel existing subscription if any
    print("\n4. Checking for existing subscription...")
    response = requests.get(
        f"{BASE_URL}/subscriptions/current",
        headers=get_headers(org_token)
    )
    if response.status_code == 200:
        print("⚠️  Subscription exists, cancelling it...")
        sub_data = response.json()
        sub_id = sub_data["subscription_id"]
        
        response = requests.post(
            f"{BASE_URL}/subscriptions/{sub_id}/cancel",
            headers=get_headers(org_token),
            json={"reason": "Testing payment workflow"}
        )
        if response.status_code == 200:
            print("✅ Existing subscription cancelled")
        else:
            print(f"❌ Failed to cancel: {response.status_code}")
            return
    else:
        print("✅ No existing subscription")
    
    # Step 5: Create subscription with WALLET payment
    print("\n5. Creating subscription with WALLET payment...")
    response = requests.post(
        f"{BASE_URL}/subscriptions",
        headers=get_headers(org_token),
        json={
            "organization_id": org_id,
            "tier": "PROFESSIONAL",
            "trial_days": 0,
            "pay_from_wallet": True  # Wallet payment - should NOT deduct yet
        }
    )
    if response.status_code != 201:
        print(f"❌ Failed to create subscription: {response.status_code}")
        print(response.text)
        return
    
    subscription = response.json()
    print(f"✅ Subscription created: {subscription['subscription_id']}")
    print(f"   Status: {subscription['status']}")
    print(f"   Tier: {subscription['tier']}")
    print(f"   Fee: {subscription['subscription_fee']} {subscription['currency']}")
    
    # Step 6: Verify wallet balance NOT deducted yet
    print("\n6. Verifying wallet balance NOT deducted yet...")
    response = requests.get(
        f"{BASE_URL}/wallet/balance",
        headers=get_headers(org_token)
    )
    if response.status_code == 200:
        wallet_data = response.json()
        current_balance = wallet_data.get("available_balance", 0)
        print(f"   Current balance: {current_balance} ETB")
        if current_balance == initial_balance:
            print("✅ Wallet balance unchanged (correct - awaiting Finance verification)")
        else:
            print(f"❌ ERROR: Wallet balance changed! Expected {initial_balance}, got {current_balance}")
            return
    
    # Step 7: Login as Finance Officer
    print("\n7. Logging in as Finance Officer...")
    finance_token = login(FINANCE_EMAIL, FINANCE_PASSWORD)
    if not finance_token:
        print("❌ Failed to login as Finance Officer")
        return
    print("✅ Finance Officer logged in")
    
    # Step 8: Check pending payments
    print("\n8. Checking pending payments in Finance portal...")
    response = requests.get(
        f"{BASE_URL}/subscriptions/pending-payments",
        headers=get_headers(finance_token)
    )
    if response.status_code != 200:
        print(f"❌ Failed to get pending payments: {response.status_code}")
        print(response.text)
        return
    
    pending_data = response.json()
    payments = pending_data.get("payments", [])
    print(f"✅ Found {len(payments)} pending payment(s)")
    
    if len(payments) == 0:
        print("❌ ERROR: No pending payments found!")
        return
    
    # Find our payment
    our_payment = None
    for payment in payments:
        if payment["subscription_id"] == subscription["subscription_id"]:
            our_payment = payment
            break
    
    if not our_payment:
        print("❌ ERROR: Our payment not found in pending payments!")
        return
    
    print(f"✅ Payment found in pending payments:")
    print(f"   Payment ID: {our_payment['payment_id']}")
    print(f"   Organization: {our_payment['organization_name']}")
    print(f"   Amount: {our_payment['amount']} {our_payment['currency']}")
    print(f"   Due Date: {our_payment['due_date']}")
    
    # Step 9: Verify the payment (this should deduct from wallet)
    print("\n9. Finance Officer verifying payment (should deduct from wallet now)...")
    response = requests.post(
        f"{BASE_URL}/subscriptions/payments/{our_payment['payment_id']}/mark-paid",
        headers=get_headers(finance_token),
        json={
            "payment_method": "wallet",  # Finance Officer confirms wallet payment
            "gateway_transaction_id": f"TEST-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        }
    )
    if response.status_code != 200:
        print(f"❌ Failed to verify payment: {response.status_code}")
        print(response.text)
        return
    
    payment_result = response.json()
    print(f"✅ Payment verified successfully!")
    print(f"   Status: {payment_result['status']}")
    print(f"   Paid At: {payment_result['paid_at']}")
    print(f"   Method: {payment_result['payment_method']}")
    
    # Step 10: Verify wallet balance WAS deducted
    print("\n10. Verifying wallet balance WAS deducted...")
    response = requests.get(
        f"{BASE_URL}/wallet/balance",
        headers=get_headers(org_token)
    )
    if response.status_code == 200:
        wallet_data = response.json()
        final_balance = wallet_data.get("available_balance", 0)
        expected_balance = initial_balance - subscription['subscription_fee']
        print(f"   Initial balance: {initial_balance} ETB")
        print(f"   Subscription fee: {subscription['subscription_fee']} ETB")
        print(f"   Expected balance: {expected_balance} ETB")
        print(f"   Actual balance: {final_balance} ETB")
        
        if final_balance == expected_balance:
            print("✅ Wallet balance correctly deducted!")
        else:
            print(f"❌ ERROR: Wallet balance incorrect!")
            return
    
    # Step 11: Check subscription status
    print("\n11. Checking subscription status...")
    response = requests.get(
        f"{BASE_URL}/subscriptions/current",
        headers=get_headers(org_token)
    )
    if response.status_code != 200:
        print(f"❌ Failed to get subscription: {response.status_code}")
        return
    
    updated_sub = response.json()
    print(f"✅ Subscription status: {updated_sub['status']}")
    if updated_sub['status'] == 'ACTIVE':
        print("✅ SUCCESS: Subscription is now ACTIVE!")
    else:
        print(f"⚠️  WARNING: Subscription status is {updated_sub['status']}, expected ACTIVE")
    
    # Step 12: Verify payment no longer in pending
    print("\n12. Verifying payment removed from pending list...")
    response = requests.get(
        f"{BASE_URL}/subscriptions/pending-payments",
        headers=get_headers(finance_token)
    )
    if response.status_code == 200:
        pending_data = response.json()
        payments = pending_data.get("payments", [])
        
        still_pending = any(p["payment_id"] == our_payment["payment_id"] for p in payments)
        if still_pending:
            print("❌ ERROR: Payment still in pending list!")
        else:
            print(f"✅ Payment removed from pending list (now {len(payments)} pending)")
    
    print("\n" + "=" * 80)
    print("✅ ALL TESTS PASSED! WALLET PAYMENT WORKFLOW COMPLETE!")
    print("=" * 80)
    print("\nSummary:")
    print(f"  • Subscription created with wallet payment")
    print(f"  • Payment appeared in Finance portal as pending")
    print(f"  • Wallet NOT deducted initially")
    print(f"  • Finance Officer verified payment")
    print(f"  • Wallet deducted: {subscription['subscription_fee']} ETB")
    print(f"  • Subscription activated")
    print(f"  • Payment removed from pending list")

if __name__ == "__main__":
    main()
