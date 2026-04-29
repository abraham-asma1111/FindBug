"""
Check user account and KYC verification status
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from src.core.database import SessionLocal
from src.domain.models.kyc import KYCVerification
from src.domain.models.user import User

def check_user_status(email: str):
    """Check user account and KYC status"""
    db: Session = SessionLocal()
    
    try:
        # Find user
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            print(f"❌ User not found: {email}")
            return
        
        print(f"✅ Found user: {user.email}")
        print(f"\n📋 User Account Status:")
        print(f"   ID: {user.id}")
        print(f"   Email: {user.email}")
        print(f"   Email Verified At: {user.email_verified_at}")
        print(f"   Is Active: {user.is_active}")
        print(f"   Role: {user.role}")
        print(f"   Created: {user.created_at}")
        
        # Find KYC record
        kyc = db.query(KYCVerification).filter(
            KYCVerification.user_id == user.id
        ).first()
        
        print(f"\n📋 KYC Verification Status:")
        if not kyc:
            print("   ❌ No KYC record found")
            print("   Status would be: not_started")
        else:
            print(f"   Status: {kyc.status}")
            print(f"   Persona Inquiry ID: {kyc.persona_inquiry_id}")
            print(f"   Persona Status: {kyc.persona_status}")
            print(f"   Persona Template ID: {kyc.persona_template_id}")
            print(f"   Submitted At: {kyc.submitted_at}")
            print(f"   Verified At: {kyc.verified_at}")
            print(f"   Persona Verified At: {kyc.persona_verified_at}")
            if kyc.rejection_reason:
                print(f"   Rejection Reason: {kyc.rejection_reason}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python check_user_verification.py <user_email>")
        print("Example: python check_user_verification.py researcher@example.com")
        sys.exit(1)
    
    email = sys.argv[1]
    check_user_status(email)
