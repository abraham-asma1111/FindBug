#!/usr/bin/env python3
"""Check KYC status for researcher@test.com"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.core.database import SessionLocal
from src.domain.models.kyc import KYCVerification
from src.domain.models.user import User

def check_researcher_kyc():
    db = SessionLocal()
    try:
        # Find user
        user = db.query(User).filter(User.email == "researcher@test.com").first()
        
        if not user:
            print("❌ User researcher@test.com not found")
            return
        
        print(f"✅ User found: {user.email} (ID: {user.id})")
        
        # Find KYC record
        kyc = db.query(KYCVerification).filter(
            KYCVerification.user_id == user.id
        ).first()
        
        if not kyc:
            print("❌ No KYC record found for this user")
            return
        
        print(f"\n📋 KYC Record:")
        print(f"  - Status: {kyc.status}")
        print(f"  - Email Verified: {kyc.email_verified}")
        print(f"  - Email Address: {kyc.email_address}")
        print(f"  - Email Verified At: {kyc.email_verified_at}")
        print(f"  - Persona Status: {kyc.persona_status}")
        print(f"  - Persona Inquiry ID: {kyc.persona_inquiry_id}")
        
    finally:
        db.close()

if __name__ == "__main__":
    check_researcher_kyc()
