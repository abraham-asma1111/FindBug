"""Test wallet recharge functionality for organization."""
import requests
import json

BASE_URL = "http://127.0.0.1:8002/api/v1"

# Organization credentials
ORG_EMAIL = "org@test.com"
ORG_PASSWORD = "Password123!"

def test_wallet_recharge():
    """Test the complete wallet recharge workflow."""
    
    print("=" * 60)
    print("WALLET RECHARGE TEST")
    print("=" * 60)
    
    # Step 1: Login as organization
    print("\n1. Logging in as organization...")
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": ORG_EMAIL,
            "password": ORG_PASSWORD
        }
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(f"Response: {login_response.text}")
        return
    
    login_data = login_response.json()
    access_token = login_data.get("access_token")
    print(f"✅ Login successful")
    print(f"   User: {login_data.get('user', {}).get('email')}")
    print(f"   Role: {login_data.get('user', {}).get('role')}")
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # Step 2: Get current wallet balance
    print("\n2. Getting current wallet balance...")
    balance_response = requests.get(
        f"{BASE_URL}/wallet/balance",
        headers=headers
    )
    
    if balance_response.status_code != 200:
        print(f"❌ Failed to get balance: {balance_response.status_code}")
        print(f"Response: {balance_response.text}")
        return
    
    balance_data = balance_response.json()
    print(f"✅ Current balance retrieved")
    print(f"   Balance: {balance_data.get('balance', 0)} ETB")
    print(f"   Available: {balance_data.get('available_balance', 0)} ETB")
    print(f"   Reserved: {balance_data.get('reserved_balance', 0)} ETB")
    
    initial_balance = balance_data.get('balance', 0)
    
    # Step 3: Recharge wallet
    print("\n3. Recharging wallet with 5000 ETB...")
    recharge_amount = 5000
    payment_method = "bank_transfer"
    
    recharge_response = requests.post(
        f"{BASE_URL}/wallet/recharge?amount={recharge_amount}&payment_method={payment_method}",
        headers=headers
    )
    
    if recharge_response.status_code != 201:
        print(f"❌ Recharge failed: {recharge_response.status_code}")
        print(f"Response: {recharge_response.text}")
        return
    
    recharge_data = recharge_response.json()
    print(f"✅ Recharge successful")
    print(f"   Transaction ID: {recharge_data.get('transaction_id')}")
    print(f"   Amount: {recharge_data.get('amount')} ETB")
    print(f"   Payment Method: {recharge_data.get('payment_method')}")
    print(f"   New Balance: {recharge_data.get('new_balance')} ETB")
    print(f"   Status: {recharge_data.get('status')}")
    
    # Step 4: Verify new balance
    print("\n4. Verifying new balance...")
    balance_response = requests.get(
        f"{BASE_URL}/wallet/balance",
        headers=headers
    )
    
    if balance_response.status_code != 200:
        print(f"❌ Failed to get balance: {balance_response.status_code}")
        return
    
    balance_data = balance_response.json()
    new_balance = balance_data.get('balance', 0)
    
    print(f"✅ Balance verified")
    print(f"   Previous Balance: {initial_balance} ETB")
    print(f"   Recharge Amount: {recharge_amount} ETB")
    print(f"   New Balance: {new_balance} ETB")
    print(f"   Expected: {initial_balance + recharge_amount} ETB")
    
    if new_balance == initial_balance + recharge_amount:
        print(f"   ✅ Balance matches expected amount!")
    else:
        print(f"   ❌ Balance mismatch!")
    
    # Step 5: Get transaction history
    print("\n5. Getting transaction history...")
    transactions_response = requests.get(
        f"{BASE_URL}/wallet/transactions?limit=5",
        headers=headers
    )
    
    if transactions_response.status_code != 200:
        print(f"❌ Failed to get transactions: {transactions_response.status_code}")
        return
    
    transactions_data = transactions_response.json()
    transactions = transactions_data.get('transactions', [])
    
    print(f"✅ Transaction history retrieved")
    print(f"   Total transactions: {len(transactions)}")
    
    if transactions:
        print("\n   Recent transactions:")
        for tx in transactions[:3]:
            print(f"   - Type: {tx.get('transaction_type')}, Amount: {tx.get('amount')} ETB, "
                  f"Reference: {tx.get('reference_type')}, Balance After: {tx.get('balance_after')} ETB")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    test_wallet_recharge()
