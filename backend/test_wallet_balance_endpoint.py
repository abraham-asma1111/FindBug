"""
Test wallet balance endpoint.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import requests
import json

def test_wallet_balance():
    """Test wallet balance endpoint."""
    
    print("\n" + "="*80)
    print("WALLET BALANCE ENDPOINT TEST")
    print("="*80)
    
    # Login first
    print("\n[1] Logging in as org@example.com...")
    login_response = requests.post(
        "http://127.0.0.1:8002/api/v1/auth/login",
        json={
            "email": "org@example.com",
            "password": "Password123!"
        }
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(login_response.text)
        return
    
    token = login_response.json()["access_token"]
    print(f"✅ Login successful")
    
    # Get wallet balance
    print("\n[2] Getting wallet balance...")
    headers = {"Authorization": f"Bearer {token}"}
    
    balance_response = requests.get(
        "http://127.0.0.1:8002/api/v1/wallet/balance",
        headers=headers
    )
    
    print(f"Status: {balance_response.status_code}")
    
    if balance_response.status_code == 200:
        balance_data = balance_response.json()
        print(f"✅ Balance retrieved successfully:")
        print(f"   Wallet ID: {balance_data.get('wallet_id')}")
        print(f"   Balance: {balance_data.get('balance')} {balance_data.get('currency')}")
        print(f"   Available: {balance_data.get('available_balance')} {balance_data.get('currency')}")
        print(f"   Reserved: {balance_data.get('reserved_balance')} {balance_data.get('currency')}")
    else:
        print(f"❌ Failed to get balance: {balance_response.status_code}")
        print(balance_response.text)
    
    # Get transaction history
    print("\n[3] Getting transaction history...")
    
    transactions_response = requests.get(
        "http://127.0.0.1:8002/api/v1/wallet/transactions",
        headers=headers
    )
    
    print(f"Status: {transactions_response.status_code}")
    
    if transactions_response.status_code == 200:
        transactions_data = transactions_response.json()
        print(f"✅ Transactions retrieved successfully:")
        print(f"   Total: {transactions_data.get('total')}")
        
        for tx in transactions_data.get('transactions', [])[:5]:
            print(f"\n   - {tx['transaction_type']}: {tx['amount']} ETB")
            print(f"     Balance After: {tx['balance_after']}")
            print(f"     Reference: {tx['reference_type']}")
            print(f"     Status: {tx['status']}")
    else:
        print(f"❌ Failed to get transactions: {transactions_response.status_code}")
        print(transactions_response.text)
    
    print("\n" + "="*80)

if __name__ == "__main__":
    test_wallet_balance()
