#!/usr/bin/env python3
"""
Test script to add payment method for researcher after KYC verification.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy.orm import Session
from src.core.database import SessionLocal
from src.services.payment_service import PaymentService
from src.services.kyc_service import KYCService
from src.domain.models.user import User

def test_add_payment_method():
    """Test adding payment method for KYC-verified researcher."""
    db: Session = SessionLocal()
    
    try:
        # Get the test researcher user
        user = db.query(User).filter(User.email == "foyihob867@justnapa.com").first()
        
        if not user:
            print("❌ User not found")
            return
        
        print(f"✅ Found user: {user.email} (ID: {user.id})")
        
        # Check KYC status
        kyc_service = KYCService(db)
        kyc_status = kyc_service.get_kyc_status(str(user.id))
        
        print(f"\n📋 KYC Status:")
        print(f"   Status: {kyc_status['status']}")
        print(f"   Persona: {kyc_status.get('persona_status', 'N/A')}")
        print(f"   Email Verified: {kyc_status.get('email_verified', False)}")
        
        if kyc_status["status"] != "approved":
            print(f"\n⚠️  KYC not approved. Cannot add payment methods.")
            print(f"   Current status: {kyc_status['status']}")
            return
        
        # Get existing payment methods
        payment_service = PaymentService(db)
        existing_methods = payment_service.get_user_payment_methods(str(user.id))
        
        print(f"\n💳 Existing Payment Methods: {len(existing_methods)}")
        for method in existing_methods:
            print(f"   - {method.method_type}: {method.account_name} (****{method.account_number[-4:]})")
            print(f"     Default: {method.is_default}, Verified: {method.is_verified}")
        
        # Add a new payment method (Ethiopian bank account)
        print(f"\n➕ Adding new payment method...")
        
        new_method_data = {
            "method_type": "bank_account",
            "account_name": "Test Researcher",
            "account_number": "1000123456789",
            "bank_name": "Commercial Bank of Ethiopia",
            "is_default": len(existing_methods) == 0  # Set as default if first method
        }
        
        new_method = payment_service.add_payment_method(str(user.id), new_method_data)
        
        print(f"✅ Payment method added successfully!")
        print(f"   ID: {new_method.id}")
        print(f"   Type: {new_method.method_type}")
        print(f"   Account: {new_method.account_name}")
        print(f"   Bank: {new_method.bank_name}")
        print(f"   Number: ****{new_method.account_number[-4:]}")
        print(f"   Default: {new_method.is_default}")
        print(f"   Verified: {new_method.is_verified}")
        
        # Get updated list
        updated_methods = payment_service.get_user_payment_methods(str(user.id))
        print(f"\n💳 Total Payment Methods: {len(updated_methods)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_add_payment_method()
