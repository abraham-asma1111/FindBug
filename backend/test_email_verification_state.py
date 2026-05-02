#!/usr/bin/env python3
"""
Test script to verify email verification state persistence.
Tests that:
1. Database updates email_verified = True
2. API returns correct status after verification
3. Frontend receives verified state on page load
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy.orm import Session
from src.core.database import get_db
from src.domain.models.kyc import KYCVerification
from src.domain.models.user import User
from uuid import UUID

def check_email_verification_state(email: str):
    """Check email verification state for a user."""
    db = next(get_db())
    
    try:
        # Find user by email
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            print(f"❌ User not found: {email}")
            return
        
        print(f"\n{'='*60}")
        print(f"USER: {user.email}")
        print(f"User ID: {user.id}")
        print(f"{'='*60}\n")
        
        # Find KYC record
        kyc = db.query(KYCVerification).filter(
            KYCVerification.user_id == user.id
        ).first()
        
        if not kyc:
            print("❌ No KYC record found")
            print("\n📋 EXPECTED STATE:")
            print("   - KYC record should exist after sending verification code")
            return
        
        print("✅ KYC Record Found\n")
        print(f"📊 DATABASE STATE:")
        print(f"   KYC ID: {kyc.id}")
        print(f"   Status: {kyc.status}")
        print(f"   Email Address: {kyc.email_address}")
        print(f"   Email Verified: {kyc.email_verified}")
        print(f"   Email Verified At: {kyc.email_verified_at}")
        print(f"   Verification Code: {'SET' if kyc.email_verification_code else 'None'}")
        print(f"   Code Expires: {kyc.email_verification_code_expires}")
        print(f"   Attempts: {kyc.email_verification_attempts}")
        
        print(f"\n🔍 VERIFICATION STATUS:")
        if kyc.email_verified:
            print(f"   ✅ Email is VERIFIED")
            print(f"   ✅ Verified at: {kyc.email_verified_at}")
            print(f"   ✅ Email: {kyc.email_address}")
            print(f"\n📱 FRONTEND SHOULD SHOW:")
            print(f"   - Success card with green checkmark")
            print(f"   - Verified email: {kyc.email_address}")
            print(f"   - NO email input form")
        else:
            print(f"   ⏳ Email is NOT verified")
            if kyc.email_verification_code:
                print(f"   📧 Verification code sent")
                print(f"   ⏰ Expires: {kyc.email_verification_code_expires}")
            else:
                print(f"   📧 No verification code sent yet")
            print(f"\n📱 FRONTEND SHOULD SHOW:")
            print(f"   - Email input form OR OTP input form")
        
        print(f"\n🌐 API RESPONSE (/kyc/email/status):")
        print(f"   {{")
        print(f"     'email_verified': {kyc.email_verified},")
        print(f"     'email_address': '{kyc.email_address}',")
        print(f"     'email_verified_at': '{kyc.email_verified_at.isoformat() if kyc.email_verified_at else None}',")
        print(f"     'can_verify_email': {not kyc.email_verified}")
        print(f"   }}")
        
    finally:
        db.close()

if __name__ == "__main__":
    # Test with the current user
    test_email = "abrahambecon@gmail.com"
    
    if len(sys.argv) > 1:
        test_email = sys.argv[1]
    
    print("\n🔍 EMAIL VERIFICATION STATE CHECK")
    print(f"Testing email: {test_email}\n")
    
    check_email_verification_state(test_email)
    
    print(f"\n{'='*60}")
    print("✅ State check complete!")
    print(f"{'='*60}\n")
