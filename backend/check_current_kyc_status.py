#!/usr/bin/env python3
"""
Check current KYC status for the logged-in user
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.domain.models.kyc import KYCVerification
from src.domain.models.user import User
from uuid import UUID

# Database connection
DATABASE_URL = "postgresql://bugbounty_user:changeme123@localhost:5432/bug_bounty_production"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def check_status():
    """Check KYC status for user"""
    db = SessionLocal()
    
    try:
        # Get the user by email
        user = db.query(User).filter(User.email == 'abrahambecon@gmail.com').first()
        
        if not user:
            print("❌ User 'abrahambecon@gmail.com' not found")
            print("Trying to find any researcher...")
            user = db.query(User).filter(User.role == 'RESEARCHER').order_by(User.created_at.desc()).first()
            if not user:
                print("❌ No researcher user found")
                return
        
        print("=" * 80)
        print(f"USER: {user.email}")
        print(f"USER ID: {user.id}")
        print("=" * 80)
        print()
        
        # Get KYC record
        kyc = db.query(KYCVerification).filter(
            KYCVerification.user_id == user.id
        ).order_by(KYCVerification.created_at.desc()).first()
        
        if not kyc:
            print("❌ No KYC record found")
            return
        
        print("DATABASE VALUES:")
        print(f"  status:              {kyc.status}")
        print(f"  persona_status:      {kyc.persona_status}")
        print(f"  persona_inquiry_id:  {kyc.persona_inquiry_id}")
        print(f"  phone_verified:      {kyc.phone_verified}")
        print(f"  phone_number:        {kyc.phone_number}")
        print()
        
        # Calculate what API should return
        can_verify_phone = kyc.status == "approved" and not kyc.phone_verified
        
        print("API RESPONSE (/kyc/persona/status):")
        print(f"  status:              {kyc.status}")
        print(f"  persona_status:      {kyc.persona_status}")
        print(f"  phone_verified:      {kyc.phone_verified or False}")
        print(f"  can_verify_phone:    {can_verify_phone}")
        print()
        
        print("FRONTEND STATUS:")
        print(f"  Step 1 (Persona):    {'✅ COMPLETE' if kyc.persona_status in ['completed', 'approved'] else '❌ INCOMPLETE'}")
        print(f"  Step 2 (SMS):        {'🔓 UNLOCKED' if can_verify_phone else '🔒 LOCKED'}")
        print()
        
        if can_verify_phone:
            print("✅ SMS verification should be UNLOCKED")
            print("   You can now enter your phone number and send SMS code")
        else:
            print("❌ SMS verification is LOCKED")
            if kyc.status != "approved":
                print(f"   Reason: KYC status is '{kyc.status}' (needs to be 'approved')")
            if kyc.phone_verified:
                print("   Reason: Phone already verified")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_status()
