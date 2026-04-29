"""
Reset KYC status for a user to start fresh with Persona verification
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from src.core.database import SessionLocal
from src.domain.models.kyc import KYCVerification
from src.domain.models.user import User

def reset_kyc_status(email: str):
    """Reset KYC status for a user"""
    db: Session = SessionLocal()
    
    try:
        # Find user
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            print(f"❌ User not found: {email}")
            return
        
        print(f"✅ Found user: {user.email} (ID: {user.id})")
        
        # Find KYC record
        kyc = db.query(KYCVerification).filter(
            KYCVerification.user_id == user.id
        ).first()
        
        if not kyc:
            print("ℹ️  No KYC record found - user can start fresh")
            return
        
        print(f"\n📋 Current KYC Status:")
        print(f"   Status: {kyc.status}")
        print(f"   Persona Status: {kyc.persona_status}")
        print(f"   Persona Inquiry ID: {kyc.persona_inquiry_id}")
        
        # Delete the KYC record to start fresh
        db.delete(kyc)
        db.commit()
        
        print(f"\n✅ KYC record deleted - user can now start fresh verification")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python reset_kyc_status.py <user_email>")
        print("Example: python reset_kyc_status.py researcher@example.com")
        sys.exit(1)
    
    email = sys.argv[1]
    reset_kyc_status(email)
