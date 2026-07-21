#!/usr/bin/env python3
"""
Fix Email Hijacking Issue - Security Fix

This script identifies and fixes KYC records where the verified email
doesn't match the user's registered email (email hijacking vulnerability).
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy.orm import Session
from src.core.database import SessionLocal
from src.domain.models.kyc import KYCVerification
from src.domain.models.user import User

def fix_email_hijacking():
    """Find and fix email hijacking issues"""
    db: Session = SessionLocal()
    
    try:
        print("=" * 80)
        print("EMAIL HIJACKING SECURITY FIX")
        print("=" * 80)
        print()
        
        # Find all KYC records with verified emails
        kyc_records = db.query(KYCVerification).filter(
            KYCVerification.email_verified == True
        ).all()
        
        print(f"Found {len(kyc_records)} KYC records with verified emails")
        print()
        
        issues_found = 0
        fixed_count = 0
        
        for kyc in kyc_records:
            # Get the user
            user = db.query(User).filter(User.id == kyc.user_id).first()
            
            if not user:
                print(f"⚠️  WARNING: KYC record {kyc.id} has no associated user!")
                continue
            
            # Check if email matches
            if kyc.email_address and kyc.email_address.lower() != user.email.lower():
                issues_found += 1
                print(f"🚨 SECURITY ISSUE FOUND:")
                print(f"   User ID: {user.id}")
                print(f"   User Email (registered): {user.email}")
                print(f"   KYC Email (verified): {kyc.email_address}")
                print(f"   Status: Email hijacking detected!")
                print()
                
                # Ask user what to do
                print("   Options:")
                print("   1. Reset email verification (user must re-verify their registered email)")
                print("   2. Update KYC email to match registered email (keep verified status)")
                print("   3. Skip this record")
                choice = input("   Enter choice (1/2/3): ").strip()
                
                if choice == "1":
                    # Reset verification
                    kyc.email_verified = False
                    kyc.email_verified_at = None
                    kyc.email_address = None
                    kyc.email_verification_code = None
                    kyc.email_verification_code_expires = None
                    kyc.email_verification_attempts = 0
                    db.commit()
                    fixed_count += 1
                    print("   ✅ Reset email verification - user must re-verify")
                    print()
                    
                elif choice == "2":
                    # Update to registered email
                    kyc.email_address = user.email
                    db.commit()
                    fixed_count += 1
                    print(f"   ✅ Updated KYC email to {user.email}")
                    print()
                    
                else:
                    print("   ⏭️  Skipped")
                    print()
            else:
                print(f"✅ User {user.email}: Email matches (OK)")
        
        print()
        print("=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"Total KYC records checked: {len(kyc_records)}")
        print(f"Security issues found: {issues_found}")
        print(f"Records fixed: {fixed_count}")
        print()
        
        if issues_found == 0:
            print("✅ No email hijacking issues found!")
        elif fixed_count == issues_found:
            print("✅ All issues have been fixed!")
        else:
            print(f"⚠️  {issues_found - fixed_count} issues remain unfixed")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    fix_email_hijacking()
