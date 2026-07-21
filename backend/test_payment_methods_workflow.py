#!/usr/bin/env python3
"""
Test Payment Methods Workflow
Tests the complete payment methods functionality for researchers.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
TEST_USER_EMAIL = "researcher@example.com"
TEST_USER_PASSWORD = "password123"

def print_step(step_num, description):
    """Print test step with formatting"""
    print(f"\n{'='*60}")
    print(f"STEP {step_num}: {description}")
    print('='*60)

def print_result(success, message, data=None):
    """Print test result with formatting"""
    status = "✅ SUCCESS" if success else "❌ FAILED"
    print(f"{status}: {message}")
    if data:
        print(f"Data: {json.dumps(data, indent=2)}")

def authenticate():
    """Authenticate and get access token"""
    print_step(1, "Authentication")
    
    # Login
    login_data = {
        "username": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data.get("access_token")
        print_result(True, "Authentication successful")
        return access_token
    else:
        print_result(False, f"Authentication failed: {response.text}")
        return None

def get_user_profile(token):
    """Get user profile to get user ID"""
    print_step(2, "Get User Profile")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    
    if response.status_code == 200:
        user_data = response.json()
        user_id = user_data.get("id")
        print_result(True, f"User profile retrieved, ID: {user_id}")
        return user_id
    else:
        print_result(False, f"Failed to get user profile: {response.text}")
        return None

def check_kyc_status(token, user_id):
    """Check KYC verification status"""
    print_step(3, "Check KYC Status")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/kyc/{user_id}/status", headers=headers)
    
    if response.status_code == 200:
        kyc_data = response.json()
        status = kyc_data.get("status")
        print_result(True, f"KYC status: {status}")
        return status == "approved"
    else:
        print_result(False, f"Failed to check KYC status: {response.text}")
        return False

def get_payment_methods(token, user_id):
    """Get existing payment methods"""
    print_step(4, "Get Payment Methods")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/payment-methods/{user_id}", headers=headers)
    
    if response.status_code == 200:
        methods = response.json()
        print_result(True, f"Retrieved {len(methods)} payment methods", methods)
        return methods
    elif response.status_code == 403:
        print_result(False, "KYC verification required to access payment methods")
        return None
    else:
        print_result(False, f"Failed to get payment methods: {response.text}")
        return None

def add_bank_payment_method(token, user_id):
    """Add a bank transfer payment method"""
    print_step(5, "Add Bank Transfer Payment Method")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    method_data = {
        "method_type": "bank_transfer",
        "account_name": "John Doe",
        "account_number": "1234567890123456",
        "bank_name": "Commercial Bank of Ethiopia",
        "is_default": True
    }
    
    response = requests.post(
        f"{BASE_URL}/payment-methods/{user_id}",
        headers=headers,
        json=method_data
    )
    
    if response.status_code == 200:
        method = response.json()
        method_id = method.get("id")
        print_result(True, f"Bank payment method added, ID: {method_id}", method)
        return method_id
    elif response.status_code == 403:
        print_result(False, "KYC verification required to add payment methods")
        return None
    else:
        print_result(False, f"Failed to add bank payment method: {response.text}")
        return None

def add_telebirr_payment_method(token, user_id):
    """Add a Telebirr payment method"""
    print_step(6, "Add Telebirr Payment Method")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    method_data = {
        "method_type": "telebirr",
        "account_name": "John Doe",
        "account_number": "+251911123456",
        "phone_number": "+251911123456",
        "is_default": False
    }
    
    response = requests.post(
        f"{BASE_URL}/payment-methods/{user_id}",
        headers=headers,
        json=method_data
    )
    
    if response.status_code == 200:
        method = response.json()
        method_id = method.get("id")
        print_result(True, f"Telebirr payment method added, ID: {method_id}", method)
        return method_id
    else:
        print_result(False, f"Failed to add Telebirr payment method: {response.text}")
        return None

def set_default_payment_method(token, method_id, user_id):
    """Set a payment method as default"""
    print_step(7, "Set Default Payment Method")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(
        f"{BASE_URL}/payment-methods/{method_id}/set-default",
        headers=headers,
        json={"user_id": user_id}
    )
    
    if response.status_code == 200:
        result = response.json()
        print_result(True, "Default payment method updated", result)
        return True
    else:
        print_result(False, f"Failed to set default payment method: {response.text}")
        return False

def update_payment_method(token, method_id):
    """Update a payment method"""
    print_step(8, "Update Payment Method")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    update_data = {
        "account_name": "John Doe Updated",
        "bank_name": "Awash International Bank"
    }
    
    response = requests.put(
        f"{BASE_URL}/payment-methods/{method_id}",
        headers=headers,
        json=update_data
    )
    
    if response.status_code == 200:
        method = response.json()
        print_result(True, "Payment method updated", method)
        return True
    else:
        print_result(False, f"Failed to update payment method: {response.text}")
        return False

def delete_payment_method(token, method_id):
    """Delete a payment method"""
    print_step(9, "Delete Payment Method")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.delete(f"{BASE_URL}/payment-methods/{method_id}", headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print_result(True, "Payment method deleted", result)
        return True
    else:
        print_result(False, f"Failed to delete payment method: {response.text}")
        return False

def main():
    """Run the complete payment methods workflow test"""
    print("🧪 PAYMENT METHODS WORKFLOW TEST")
    print(f"Testing against: {BASE_URL}")
    print(f"Test user: {TEST_USER_EMAIL}")
    print(f"Started at: {datetime.now()}")
    
    # Step 1: Authenticate
    token = authenticate()
    if not token:
        print("\n❌ Test failed: Could not authenticate")
        sys.exit(1)
    
    # Step 2: Get user profile
    user_id = get_user_profile(token)
    if not user_id:
        print("\n❌ Test failed: Could not get user profile")
        sys.exit(1)
    
    # Step 3: Check KYC status
    kyc_approved = check_kyc_status(token, user_id)
    if not kyc_approved:
        print("\n⚠️  Warning: KYC not approved. Some operations may fail.")
    
    # Step 4: Get existing payment methods
    existing_methods = get_payment_methods(token, user_id)
    if existing_methods is None and kyc_approved:
        print("\n❌ Test failed: Could not get payment methods")
        sys.exit(1)
    
    if not kyc_approved:
        print("\n✅ Test completed with KYC verification required")
        print("To test payment methods functionality:")
        print("1. Complete KYC verification for the test user")
        print("2. Run this test again")
        return
    
    # Step 5: Add bank payment method
    bank_method_id = add_bank_payment_method(token, user_id)
    if not bank_method_id:
        print("\n❌ Test failed: Could not add bank payment method")
        sys.exit(1)
    
    # Step 6: Add Telebirr payment method
    telebirr_method_id = add_telebirr_payment_method(token, user_id)
    if not telebirr_method_id:
        print("\n❌ Test failed: Could not add Telebirr payment method")
        sys.exit(1)
    
    # Step 7: Set Telebirr as default
    if not set_default_payment_method(token, telebirr_method_id, user_id):
        print("\n❌ Test failed: Could not set default payment method")
        sys.exit(1)
    
    # Step 8: Update bank payment method
    if not update_payment_method(token, bank_method_id):
        print("\n❌ Test failed: Could not update payment method")
        sys.exit(1)
    
    # Step 9: Delete Telebirr payment method
    if not delete_payment_method(token, telebirr_method_id):
        print("\n❌ Test failed: Could not delete payment method")
        sys.exit(1)
    
    # Final verification
    print_step(10, "Final Verification")
    final_methods = get_payment_methods(token, user_id)
    if final_methods is not None:
        print_result(True, f"Final state: {len(final_methods)} payment methods remaining")
    
    print(f"\n🎉 ALL TESTS PASSED!")
    print(f"Completed at: {datetime.now()}")

if __name__ == "__main__":
    main()