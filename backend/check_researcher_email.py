#!/usr/bin/env python3
"""Check researcher@test.com user and KYC data"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy.orm import Session
from src.core.database import SessionLocal
from src.domain.models.kyc import KYCVerification
from src.domain.models.user import User

def check_researcher():
    db: Session = SessionLocal()
    
    try:
        # Find researcher@test.com user
        user = db.query(User).filter(User.email == "researcher@test.com").first()
        
        if not user:
            print("❌ User researcher@test.com not found!")
            return
        
        print("=" * 80)
        print("USER INFO")
        print("=" * 80)
        print(f"User ID: {user.id}")
        print(f"Email: {user.email}")
        print(f"Role: {user.role}")
        print(f"Email Verified At: {user.email_verified_at}")
        print()
        
        # Find KYC records
        kyc_records = db.query(KYCVerification).filter(
            KYCVerification.user_id == user.id
        ).all()
        
        print("=" * 80)
        print(f"KYC RECORDS ({len(kyc_records)} found)")
        print("=" * 80)
        
        for i, kyc in enumerate(kyc_records, 1):
            print(f"\nKYC Record #{i}:")
            print(f"  ID: {kyc.id}")
            print(f"  Status: {kyc.status}")
            print(f"  Email Address: {kyc.email_address}")
            print(f"  Email Verified: {kyc.email_verified}")
            print(f"  Email Verified At: {kyc.email_verified_at}")
            print(f"  Persona Status: {kyc.persona_status}")
            print(f"  Persona Inquiry ID: {kyc.persona_inquiry_id}")
            print(f"  Created At: {kyc.created_at}")
        
        print()
        print("=" * 80)
        print("ANALYSIS")
        print("=" * 80)
        
        if not kyc_records:
            print("✅ No KYC records - user needs to start verification")
        else:
            latest_kyc = kyc_records[-1]  # Most recent
            
            if latest_kyc.email_verified:
                if latest_kyc.email_address == user.email:
                    print(f"✅ Email verified correctly: {latest_kyc.email_address}")
                else:
                    print(f"🚨 EMAIL MISMATCH!")
                    print(f"   User email: {user.email}")
                    print(f"   KYC email: {latest_kyc.email_address}")
            else:
                print("⚠️  Email not verified yet")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_researcher()
