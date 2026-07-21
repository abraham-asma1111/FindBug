"""
Test Bounty Payment Processing Endpoint
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8002/api/v1"

# Finance Officer credentials (you'll need to use actual credentials)
FINANCE_EMAIL = "finance@test.com"
FINANCE_PASSWORD = "password123"

def test_bounty_payment_workflow():
    """Test the complete bounty payment processing workflow."""
    
    print("\n" + "="*80)
    print("BOUNTY PAYMENT PROCESSING TEST")
    print("="*80)
    
    # Step 1: Login as Finance Officer
    print("\n[1] Logging in as Finance Officer...")
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": FINANCE_EMAIL,
            "password": FINANCE_PASSWORD
        }
    )
    
    if login_response.status_code != 200:
        print(f"   ❌ Login failed: {login_response.status_code}")
        print(f"   Response: {login_response.text}")
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"   ✅ Login successful")
    
    # Step 2: Get approved bounty payments
    print("\n[2] Fetching approved bounty payments...")
    payments_response = requests.get(
        f"{BASE_URL}/bounty-payments/approved",
        headers=headers
    )
    
    if payments_response.status_code != 200:
        print(f"   ❌ Failed to fetch payments: {payments_response.status_code}")
        print(f"   Response: {payments_response.text}")
        return
    
    payments_data = payments_response.json()
    payments = payments_data.get("bounty_payments", [])
    
    print(f"   ✅ Found {len(payments)} approved bounty payment(s)")
    
    if not payments:
        print("\n   No approved bounty payments to process.")
        return
    
    # Display payment details
    for i, payment in enumerate(payments, 1):
        print(f"\n   Payment {i}:")
        print(f"   - Payment ID: {payment['payment_id']}")
        print(f"   - Report: {payment['report']['report_number']}")
        print(f"   - Researcher: {payment['researcher']['username']}")
        print(f"   - Organization: {payment['organization']['name']}")
        print(f"   - Researcher Amount: {payment['researcher_amount']} ETB")
        print(f"   - Commission: {payment['commission_amount']} ETB")
        print(f"   - Total: {payment['total_amount']} ETB")
    
    # Step 3: Process first payment
    if payments:
        first_payment = payments[0]
        payment_id = first_payment['payment_id']
        
        print(f"\n[3] Processing payment {payment_id}...")
        process_response = requests.post(
            f"{BASE_URL}/bounty-payments/process/{payment_id}",
            headers=headers
        )
        
        if process_response.status_code != 200:
            print(f"   ❌ Failed to process payment: {process_response.status_code}")
            print(f"   Response: {process_response.text}")
            return
        
        result = process_response.json()
        print(f"   ✅ Payment processed successfully!")
        print(f"   - Researcher received: {result['researcher_amount']} ETB")
        print(f"   - Commission kept: {result['commission_kept']} ETB")
        print(f"   - Status: {result['status']}")
    
    # Step 4: Verify payment was processed
    print("\n[4] Verifying payment was processed...")
    verify_response = requests.get(
        f"{BASE_URL}/bounty-payments/approved",
        headers=headers
    )
    
    if verify_response.status_code == 200:
        remaining_payments = verify_response.json().get("bounty_payments", [])
        print(f"   ✅ Remaining approved payments: {len(remaining_payments)}")
    
    print("\n" + "="*80)
    print("✅ TEST COMPLETE")
    print("="*80 + "\n")

if __name__ == "__main__":
    test_bounty_payment_workflow()
