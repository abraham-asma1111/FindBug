#!/usr/bin/env python3
"""
Finance Portal Workflow Test Script
Tests complete workflow: Dashboard → Payments → Payouts → KYC
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8002/api/v1"

# Test credentials
ADMIN_EMAIL = "admin@securecrowd.com"
ADMIN_PASSWORD = "Admin123!@#"

def print_section(title):
    """Print section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def login():
    """Login and get access token"""
    print_section("1. LOGIN AS FINANCE OFFICER")
    
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        token = data.get("access_token")
        print(f"✓ Login successful")
        print(f"  Token: {token[:50]}...")
        return token
    else:
        print(f"✗ Login failed: {response.status_code}")
        print(f"  Response: {response.text}")
        return None

def test_dashboard_analytics(token):
    """Test dashboard analytics endpoint"""
    print_section("2. DASHBOARD ANALYTICS")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/payments/analytics?range=30d",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        stats = data.get("stats", {})
        
        print(f"✓ Analytics loaded successfully")
        print(f"\n  KPI Metrics:")
        print(f"    Total Payments: {stats.get('total_payments', 0)}")
        print(f"    Total Amount: ${stats.get('total_amount', 0):,.2f} ETB")
        print(f"    Avg Payment: ${stats.get('avg_payment', 0):,.2f} ETB")
        print(f"    Total Commission: ${stats.get('total_commission', 0):,.2f} ETB")
        
        trends = data.get("payment_trends", [])
        print(f"\n  Payment Trends: {len(trends)} data points")
        
        severity = data.get("severity_distribution", [])
        print(f"  Severity Distribution: {len(severity)} categories")
        
        researchers = data.get("top_researchers", [])
        print(f"  Top Researchers: {len(researchers)} researchers")
        
        return True
    else:
        print(f"✗ Analytics failed: {response.status_code}")
        print(f"  Response: {response.text}")
        return False

def test_payments_list(token):
    """Test payments list endpoint"""
    print_section("3. PAYMENTS LIST")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test different status filters
    statuses = ["pending", "approved", "completed"]
    
    for status in statuses:
        response = requests.get(
            f"{BASE_URL}/payments/bounty?status={status}&limit=10",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            payments = data.get("payments", [])
            print(f"✓ {status.capitalize()} payments: {len(payments)} found")
            
            if payments:
                payment = payments[0]
                print(f"    Sample: #{payment.get('transaction_id', 'N/A')[:12]}")
                print(f"    Amount: ${payment.get('researcher_amount', 0):,.2f} ETB")
                print(f"    Status: {payment.get('status', 'unknown')}")
        else:
            print(f"✗ {status.capitalize()} payments failed: {response.status_code}")

def test_payment_detail(token):
    """Test payment detail endpoint"""
    print_section("4. PAYMENT DETAIL")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # First get a payment ID
    response = requests.get(
        f"{BASE_URL}/payments/bounty?limit=1",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        payments = data.get("payments", [])
        
        if payments:
            payment_id = payments[0].get("payment_id")
            
            # Get payment details
            detail_response = requests.get(
                f"{BASE_URL}/payments/bounty/{payment_id}",
                headers=headers
            )
            
            if detail_response.status_code == 200:
                payment = detail_response.json()
                print(f"✓ Payment detail loaded")
                print(f"\n  Payment ID: {payment.get('payment_id', 'N/A')[:8]}...")
                print(f"  Transaction ID: {payment.get('transaction_id', 'N/A')}")
                print(f"  Researcher Amount: ${payment.get('researcher_amount', 0):,.2f} ETB")
                print(f"  Commission (30%): ${payment.get('commission_amount', 0):,.2f} ETB")
                print(f"  Total Amount: ${payment.get('total_amount', 0):,.2f} ETB")
                print(f"  Status: {payment.get('status', 'unknown')}")
                print(f"  Created: {payment.get('created_at', 'N/A')[:19]}")
                return True
            else:
                print(f"✗ Payment detail failed: {detail_response.status_code}")
        else:
            print("⚠ No payments found to test detail view")
    else:
        print(f"✗ Failed to get payments: {response.status_code}")
    
    return False

def test_payouts_list(token):
    """Test payouts list endpoint"""
    print_section("5. PAYOUTS LIST")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test different status filters
    statuses = ["requested", "processing", "completed"]
    
    for status in statuses:
        response = requests.get(
            f"{BASE_URL}/wallet/payouts?status={status}&limit=10",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            payouts = data.get("payouts", [])
            print(f"✓ {status.capitalize()} payouts: {len(payouts)} found")
            
            if payouts:
                payout = payouts[0]
                print(f"    Sample: #{payout.get('payout_id', 'N/A')[:8]}...")
                print(f"    Amount: ${payout.get('amount', 0):,.2f} ETB")
                print(f"    Status: {payout.get('status', 'unknown')}")
        else:
            print(f"✗ {status.capitalize()} payouts failed: {response.status_code}")

def test_payout_detail(token):
    """Test payout detail endpoint"""
    print_section("6. PAYOUT DETAIL")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # First get a payout ID
    response = requests.get(
        f"{BASE_URL}/wallet/payouts?limit=1",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        payouts = data.get("payouts", [])
        
        if payouts:
            payout_id = payouts[0].get("payout_id")
            
            # Get payout details
            detail_response = requests.get(
                f"{BASE_URL}/wallet/payouts/{payout_id}",
                headers=headers
            )
            
            if detail_response.status_code == 200:
                payout = detail_response.json()
                print(f"✓ Payout detail loaded")
                print(f"\n  Payout ID: {payout.get('payout_id', 'N/A')[:8]}...")
                print(f"  Researcher ID: {payout.get('researcher_id', 'N/A')[:8]}...")
                print(f"  Amount: ${payout.get('amount', 0):,.2f} ETB")
                print(f"  Payment Method: {payout.get('payment_method', 'N/A')}")
                print(f"  Status: {payout.get('status', 'unknown')}")
                print(f"  Created: {payout.get('created_at', 'N/A')[:19]}")
                return True
            else:
                print(f"✗ Payout detail failed: {detail_response.status_code}")
        else:
            print("⚠ No payouts found to test detail view")
    else:
        print(f"✗ Failed to get payouts: {response.status_code}")
    
    return False

def test_kyc_list(token):
    """Test KYC verifications list endpoint"""
    print_section("7. KYC VERIFICATIONS LIST")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test different status filters
    statuses = ["pending", "approved", "rejected"]
    
    for status in statuses:
        response = requests.get(
            f"{BASE_URL}/kyc/verifications?status={status}&limit=10",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            verifications = data.get("verifications", [])
            print(f"✓ {status.capitalize()} KYC: {len(verifications)} found")
            
            if verifications:
                kyc = verifications[0]
                print(f"    Sample: #{kyc.get('id', 'N/A')[:8]}...")
                print(f"    User: {kyc.get('user_name', 'Unknown')}")
                print(f"    Document: {kyc.get('document_type', 'N/A')}")
                print(f"    Status: {kyc.get('status', 'unknown')}")
        else:
            print(f"✗ {status.capitalize()} KYC failed: {response.status_code}")

def test_kyc_detail(token):
    """Test KYC verification detail endpoint"""
    print_section("8. KYC VERIFICATION DETAIL")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # First get a KYC ID
    response = requests.get(
        f"{BASE_URL}/kyc/verifications?limit=1",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        verifications = data.get("verifications", [])
        
        if verifications:
            kyc_id = verifications[0].get("id")
            
            # Get KYC details
            detail_response = requests.get(
                f"{BASE_URL}/kyc/verifications/{kyc_id}",
                headers=headers
            )
            
            if detail_response.status_code == 200:
                kyc = detail_response.json()
                print(f"✓ KYC detail loaded")
                print(f"\n  KYC ID: {kyc.get('id', 'N/A')[:8]}...")
                print(f"  User: {kyc.get('user_name', 'Unknown')}")
                print(f"  Email: {kyc.get('user_email', 'N/A')}")
                print(f"  Document Type: {kyc.get('document_type', 'N/A')}")
                print(f"  Document Number: ****{kyc.get('document_number', '')[-4:]}")
                print(f"  Status: {kyc.get('status', 'unknown')}")
                print(f"  Submitted: {kyc.get('submitted_at', 'N/A')[:19]}")
                return True
            else:
                print(f"✗ KYC detail failed: {detail_response.status_code}")
        else:
            print("⚠ No KYC verifications found to test detail view")
    else:
        print(f"✗ Failed to get KYC verifications: {response.status_code}")
    
    return False

def test_transactions(token):
    """Test transactions endpoint"""
    print_section("9. WALLET TRANSACTIONS")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/wallet/transactions?limit=10",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        transactions = data.get("transactions", [])
        print(f"✓ Transactions loaded: {len(transactions)} found")
        
        if transactions:
            txn = transactions[0]
            print(f"\n  Sample Transaction:")
            print(f"    ID: {txn.get('id', 'N/A')[:8]}...")
            print(f"    Type: {txn.get('type', 'N/A')}")
            print(f"    Amount: ${txn.get('amount', 0):,.2f} ETB")
            print(f"    Created: {txn.get('created_at', 'N/A')[:19]}")
        return True
    else:
        print(f"✗ Transactions failed: {response.status_code}")
        print(f"  Response: {response.text}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("  FINANCE PORTAL WORKFLOW TEST")
    print("  Testing Backend APIs and Database Integration")
    print("="*60)
    
    # Login
    token = login()
    if not token:
        print("\n✗ Test suite failed: Unable to login")
        return
    
    # Run tests
    results = {
        "Dashboard Analytics": test_dashboard_analytics(token),
        "Payments List": test_payments_list(token),
        "Payment Detail": test_payment_detail(token),
        "Payouts List": test_payouts_list(token),
        "Payout Detail": test_payout_detail(token),
        "KYC List": test_kyc_list(token),
        "KYC Detail": test_kyc_detail(token),
        "Transactions": test_transactions(token),
    }
    
    # Summary
    print_section("TEST SUMMARY")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}  {test_name}")
    
    print(f"\n  Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n  🎉 All tests passed! Finance Portal is working correctly.")
    else:
        print(f"\n  ⚠️  {total - passed} test(s) failed. Check the output above.")

if __name__ == "__main__":
    main()
