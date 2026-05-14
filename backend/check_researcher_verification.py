"""
Check researcher verification status
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.orm import Session
from src.core.database import SessionLocal
from src.domain.models.user import User
from src.domain.models.researcher import Researcher
from src.domain.models.kyc import KYCVerification


def check_verification():
    """Check researcher verification status."""
    db: Session = SessionLocal()
    
    try:
        print("=" * 80)
        print("RESEARCHER VERIFICATION STATUS")
        print("=" * 80)
        
        # Get all researchers
        researchers = db.query(User).filter(User.role == 'researcher').all()
        
        print(f"\nTotal Researchers: {len(researchers)}\n")
        
        for user in researchers:
            # Get researcher profile
            researcher = db.query(Researcher).filter(Researcher.user_id == user.id).first()
            
            # Get KYC status
            kyc = db.query(KYCVerification).filter(KYCVerification.user_id == user.id).first()
            
            print(f"📧 Email: {user.email}")
            print(f"   Username: {researcher.username if researcher and researcher.username else 'NOT SET'}")
            print(f"   Full Name: {user.full_name if user.full_name else 'NOT SET'}")
            print(f"   Email Verified: {'✅ YES' if user.email_verified else '❌ NO'}")
            
            if kyc:
                print(f"   KYC Status: {kyc.status.upper()}")
                print(f"   KYC Verified: {'✅ YES' if kyc.status == 'approved' else '❌ NO'}")
            else:
                print(f"   KYC Status: ❌ NO KYC RECORD")
            
            print("-" * 80)
        
        # Summary
        verified_count = db.query(User).join(KYCVerification).filter(
            User.role == 'researcher',
            KYCVerification.status == 'approved'
        ).count()
        
        print(f"\n📊 SUMMARY:")
        print(f"   Total Researchers: {len(researchers)}")
        print(f"   KYC Verified: {verified_count}")
        print(f"   Not Verified: {len(researchers) - verified_count}")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    check_verification()
