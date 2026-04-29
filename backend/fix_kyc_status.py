#!/usr/bin/env python3
"""
Fix KYC status to unlock SMS verification
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy.orm import Session
from src.core.database import SessionLocal
from src.domain.models.kyc import KYCVerification
from uuid import UUID

def fix_kyc_status():
    """Fix KYC status for user"""
    db = SessionLocal()
    
    try:
        user_id = "6a2c85a9-e707-4aec-b480-9d4fe5b69cba"
        
        # Get KYC record
        kyc = db.query(KYCVerification).filter(
            KYCVerification.user_id == UUID(user_id)
        ).order_by(KYCVerification.created_at.desc()).first()
        
        if not kyc:
            print("❌ No KYC record found")
            return
        
        print(f"📋 Current KYC Status:")
        print(f"  ID: {kyc.id}")
        print(f"  Status: {kyc.status}")
        print(f"  Persona Status: {kyc.persona_status}")
        print(f"  Persona Inquiry ID: {kyc.persona_inquiry_id}")
        print(f"  Phone Verified: {kyc.phone_verified}")
        print(f"  Phone Number: {kyc.phone_number}")
        
        # Check if needs fixing
        if kyc.persona_status == "approved" and kyc.status != "approved":
            print(f"\n🔧 Fixing status from '{kyc.status}' to 'approved'...")
            kyc.status = "approved"
            db.commit()
            print("✅ Status fixed!")
        elif kyc.status == "approved":
            print("\n✅ Status is already 'approved'")
        else:
            print(f"\n⚠️  Persona status is '{kyc.persona_status}', not 'approved'")
        
        # Show can_verify_phone logic
        can_verify = kyc.status == "approved" and not kyc.phone_verified
        print(f"\n📱 Can Verify Phone: {can_verify}")
        print(f"   (status == 'approved': {kyc.status == 'approved'})")
        print(f"   (phone_verified: {kyc.phone_verified})")
        
    finally:
        db.close()

if __name__ == "__main__":
    fix_kyc_status()
