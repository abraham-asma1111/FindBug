"""
Sync email verification status between users and KYC records.

This script ensures that users who verified their email during registration
also have their KYC email_verified flag set to True.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy.orm import Session
from src.core.database import get_db
from src.domain.models.user import User
from src.domain.models.kyc import KYCVerification

def sync_email_verification():
    """Sync email verification status from users to KYC records"""
    db = next(get_db())
    
    print("="*60)
    print("SYNC EMAIL VERIFICATION STATUS")
    print("="*60)
    print()
    
    # Find all users with verified emails
    verified_users = db.query(User).filter(
        User.email_verified_at.isnot(None)
    ).all()
    
    print(f"Found {len(verified_users)} users with verified emails")
    print()
    
    updated_count = 0
    created_count = 0
    
    for user in verified_users:
        print(f"Processing user: {user.email}")
        
        # Check if KYC record exists
        kyc = db.query(KYCVerification).filter(
            KYCVerification.user_id == user.id
        ).first()
        
        if kyc:
            # Update existing KYC record
            if not kyc.email_verified:
                kyc.email_verified = True
                kyc.email_address = user.email
                kyc.email_verified_at = user.email_verified_at
                updated_count += 1
                print(f"  ✅ Updated KYC record - email_verified = True")
            else:
                print(f"  ℹ️  Already verified in KYC")
        else:
            # Create KYC record with email verified
            kyc = KYCVerification(
                user_id=user.id,
                status="pending",  # Pending Persona verification
                email_verified=True,
                email_address=user.email,
                email_verified_at=user.email_verified_at
            )
            db.add(kyc)
            created_count += 1
            print(f"  ✅ Created KYC record with email_verified = True")
        
        print()
    
    # Commit all changes
    db.commit()
    
    print("="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Total users processed: {len(verified_users)}")
    print(f"KYC records updated: {updated_count}")
    print(f"KYC records created: {created_count}")
    print()
    print("✅ Email verification status synced successfully!")
    print("="*60)

if __name__ == "__main__":
    sync_email_verification()
