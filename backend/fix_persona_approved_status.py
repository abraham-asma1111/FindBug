#!/usr/bin/env python3
"""
Fix KYC records where Persona returned 'approved' but backend didn't recognize it
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.domain.models.kyc import KYCVerification
from datetime import datetime, timedelta

# Database connection
DATABASE_URL = "postgresql://bugbounty_user:changeme123@localhost:5432/bug_bounty_production"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def fix_approved_status():
    """Fix KYC records where persona_status is 'approved' but status is not 'approved'"""
    db = SessionLocal()
    
    try:
        print("=" * 80)
        print("FIXING PERSONA 'APPROVED' STATUS MISMATCH")
        print("=" * 80)
        print()
        
        # Find KYC records where persona_status is 'approved' but status is not 'approved'
        mismatched = db.query(KYCVerification).filter(
            KYCVerification.persona_status == 'approved',
            KYCVerification.status != 'approved'
        ).all()
        
        if not mismatched:
            print("✅ No mismatched records found. All good!")
            return
        
        print(f"Found {len(mismatched)} record(s) to fix:\n")
        
        for kyc in mismatched:
            print(f"User ID: {kyc.user_id}")
            print(f"  BEFORE:")
            print(f"    status:          {kyc.status}")
            print(f"    persona_status:  {kyc.persona_status}")
            print(f"    verified_at:     {kyc.verified_at}")
            print()
            
            # Fix the status
            kyc.status = "approved"
            if not kyc.verified_at:
                kyc.verified_at = datetime.utcnow()
            if not kyc.persona_verified_at:
                kyc.persona_verified_at = datetime.utcnow()
            if not kyc.expires_at:
                kyc.expires_at = datetime.utcnow() + timedelta(days=730)  # 2 years
            
            print(f"  AFTER:")
            print(f"    status:          {kyc.status}")
            print(f"    persona_status:  {kyc.persona_status}")
            print(f"    verified_at:     {kyc.verified_at}")
            print(f"    expires_at:      {kyc.expires_at}")
            print()
        
        # Commit changes
        db.commit()
        print("=" * 80)
        print(f"✅ Fixed {len(mismatched)} record(s)")
        print("=" * 80)
        print()
        print("Next steps:")
        print("1. Refresh your browser (F5)")
        print("2. Step 2 (SMS verification) should now be unlocked")
        print()
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    fix_approved_status()
