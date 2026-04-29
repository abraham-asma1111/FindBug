"""
Test Finance Portal Workflow End-to-End

This script tests the complete Finance Portal workflow:
1. Dashboard - Get financial overview
2. Payments - List and manage bounty payments
3. Payouts - Handle researcher payout requests
4. KYC - Manage KYC verifications
5. Transactions - View all transactions
6. Analytics - Generate financial reports
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8002/api/v1"

# Test user credentials (finance officer)
FINANCE_USER = {
    "email": "finance@securecrowd.com",
    "password": "Finance123!"
}

def login():
    """Login and get access token"""
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json=FINANCE_USER
    )
    if response.status_code == 200:
        data = response.json()
        return data.get("access_token")
    else:
        print(f"Login failed: {response.status_code} - {response.text}")
        return None

def test_dashboard(token):
    """Test Finance Dashboard - GET /payments/analytics"""
    print("\n=== TESTING FINANCE DASHBOARD ===")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/payments/analytics?range=30d",
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total Payments: {data.get('stats', {}).get('total_payments', 0)}")
        print(f"Total Amount: ${data.get('stats', {}).get('total_amount', 0)}")
        print(f"Top Researchers: {len(data.get('top_researchers', []))}")
        return True
    else:
        print(f"Error: {response.text}")
        return False

def test_payments_list(token):
    """Test Payments List - GET /payments/bounty"""
    print("\n=== TESTING PAYMENTS LIST ===")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/payments/bounty?status=approved&limit=10",
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        payments = data.get('payments', [])
        print(f"Found {len(payments)} payments")
        return True
    else:
        print(f"Error: {response.text}")
        return False

def test_payouts_list(token):
    """Test Payouts List - GET /wallet/payouts"""
    print("\n=== TESTING PAYOUTS LIST ===")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/wallet/payouts?status=requested&limit=10",
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        payouts = data.get('payouts', [])
        print(f"Found {len(payouts)} pending payouts")
        return True
    else:
        print(f"Error: {response.text}")
        return False

def test_kyc_list(token):
    """Test KYC List - GET /kyc/verifications"""
    print("\n=== TESTING KYC LIST ===")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/kyc/verifications?status=pending&limit=10",
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        verifications = data.get('verifications', [])
        print(f"Found {len(verifications)} pending KYC verifications")
        return True
    else:
        print(f"Error: {response.text}")
        return False

def test_transactions_list(token):
    """Test Transactions List - GET /wallet/transactions"""
    print("\n=== TESTING TRANSACTIONS LIST ===")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/wallet/transactions?limit=10",
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        transactions = data.get('transactions', [])
        print(f"Found {len(transactions)} transactions")
        return True
    else:
        print(f"Error: {response.text}")
        return False

def test_payment_methods(token):
    """Test Payment Methods - GET /payments/methods"""
    print("\n=== TESTING PAYMENT METHODS ===")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/payments/methods",
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        methods = data.get('payment_methods', [])
        print(f"Available payment methods: {len(methods)}")
        for method in methods:
            print(f"  - {method.get('name')}: {method.get('description')}")
        return True
    else:
        print(f"Error: {response.text}")
        return False

def main():
    """Run all Finance Portal workflow tests"""
    print("=" * 60)
    print("FINANCE PORTAL WORKFLOW TEST")
    print("=" * 60)
    
    # Login
    print("\n=== LOGGING IN ===")
    token = login()
    if not token:
        print("❌ Login failed. Cannot proceed with tests.")
        return
    
    print("✅ Login successful")
    
    # Run all tests
    results = {
        "Dashboard": test_dashboard(token),
        "Payments List": test_payments_list(token),
        "Payouts List": test_payouts_list(token),
        "KYC List": test_kyc_list(token),
        "Transactions List": test_transactions_list(token),
        "Payment Methods": test_payment_methods(token),
    }
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    total = len(results)
    passed = sum(results.values())
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All Finance Portal workflow tests passed!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")

if __name__ == "__main__":
    main()
