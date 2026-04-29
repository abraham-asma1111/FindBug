"""
Test Persona KYC status endpoint
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from src.core.database import SessionLocal
from src.domain.models.kyc import KYCVerification
from src.domain.models.user import User

def check_persona_status(email: str):
    """Check Persona KYC status for a user"""
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
            print("\n📋 Persona Status Response:")
            print({
                "status": "not_started",
                "persona_inquiry_id": None,
                "persona_status": None
            })
            return
        
        print(f"\n📋 Persona Status Response:")
        print({
            "status": kyc.status,
            "persona_inquiry_id": kyc.persona_inquiry_id,
            "persona_status": kyc.persona_status,
            "persona_verified_at": kyc.persona_verified_at.isoformat() if kyc.persona_verified_at else None,
            "verified_at": kyc.verified_at.isoformat() if kyc.verified_at else None
        })
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_persona_status.py <user_email>")
        print("Example: python test_persona_status.py researcher@example.com")
        sys.exit(1)
    
    email = sys.argv[1]
    check_persona_status(email)
