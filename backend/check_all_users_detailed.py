"""
Detailed check of ALL users in the database with verification status.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.orm import Session
from src.core.database import SessionLocal
from src.domain.models.user import User
from src.domain.models.researcher import Researcher
from src.domain.models.organization import Organization
from src.domain.models.kyc import KYCVerification


def check_all_users():
    """Check ALL users with detailed verification status."""
    db: Session = SessionLocal()
    
    try:
        print("=" * 80)
        print("COMPLETE USER DATABASE ANALYSIS")
        print("=" * 80)
        
        # Get ALL users
        all_users = db.query(User).all()
        
        print(f"\n📊 TOTAL USERS IN DATABASE: {len(all_users)}")
        print("=" * 80)
        
        # Group by role
        researchers = [u for u in all_users if u.role == 'researcher']
        organizations = [u for u in all_users if u.role == 'organization']
        finance_officers = [u for u in all_users if u.role == 'finance_officer']
        triage_specialists = [u for u in all_users if u.role == 'triage_specialist']
        admins = [u for u in all_users if u.role in ['admin', 'super_admin']]
        others = [u for u in all_users if u.role not in ['researcher', 'organization', 'finance_officer', 'triage_specialist', 'admin', 'super_admin']]
        
        print(f"\n👥 BREAKDOWN BY ROLE:")
        print(f"   • Researchers: {len(researchers)}")
        print(f"   • Organizations: {len(organizations)}")
        print(f"   • Finance Officers: {len(finance_officers)}")
        print(f"   • Triage Specialists: {len(triage_specialists)}")
        print(f"   • Admins/Super Admins: {len(admins)}")
        print(f"   • Other roles: {len(others)}")
        
        # RESEARCHERS DETAILED
        print("\n" + "=" * 80)
        print("🔬 RESEARCHERS DETAILED ANALYSIS")
        print("=" * 80)
        
        if researchers:
            for i, user in enumerate(researchers, 1):
                # Get researcher profile
                researcher_profile = db.query(Researcher).filter(Researcher.user_id == user.id).first()
                
                # Get KYC status
                kyc = db.query(KYCVerification).filter(
                    KYCVerification.user_id == user.id,
                    KYCVerification.status == 'approved'
                ).first()
                
                print(f"\n{i}. {user.email}")
                print(f"   Email Verified: {'✅ YES' if user.is_verified else '❌ NO'}")
                print(f"   KYC Verified: {'✅ YES' if kyc else '❌ NO'}")
                print(f"   Account Active: {'✅ YES' if user.is_active else '❌ NO'}")
                print(f"   Has Profile: {'✅ YES' if researcher_profile else '❌ NO'}")
                if researcher_profile:
                    print(f"   Username: {researcher_profile.username or 'Not set'}")
                print(f"   Created: {user.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print("\n   No researchers found")
        
        # ORGANIZATIONS DETAILED
        print("\n" + "=" * 80)
        print("🏢 ORGANIZATIONS DETAILED ANALYSIS")
        print("=" * 80)
        
        if organizations:
            for i, user in enumerate(organizations, 1):
                # Get organization profile
                org_profile = db.query(Organization).filter(Organization.user_id == user.id).first()
                
                # Get KYC status
                kyc = db.query(KYCVerification).filter(
                    KYCVerification.user_id == user.id,
                    KYCVerification.status == 'approved'
                ).first()
                
                print(f"\n{i}. {user.email}")
                print(f"   Email Verified: {'✅ YES' if user.is_verified else '❌ NO'}")
                print(f"   KYC Verified: {'✅ YES' if kyc else '❌ NO'}")
                print(f"   Account Active: {'✅ YES' if user.is_active else '❌ NO'}")
                print(f"   Has Profile: {'✅ YES' if org_profile else '❌ NO'}")
                if org_profile:
                    print(f"   Company Name: {org_profile.company_name or 'Not set'}")
                print(f"   Created: {user.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print("\n   No organization users found")
        
        # Check organizations table (separate from users)
        org_records = db.query(Organization).all()
        print(f"\n📋 ORGANIZATION RECORDS IN 'organizations' TABLE: {len(org_records)}")
        if org_records:
            print("\n   These are organization profiles (may or may not have user accounts):")
            for i, org in enumerate(org_records[:10], 1):
                user_link = "✅ Has User Account" if org.user_id else "❌ No User Account"
                print(f"   {i}. {org.company_name or org.email} - {user_link}")
        
        # SUMMARY
        print("\n" + "=" * 80)
        print("📊 VERIFICATION SUMMARY")
        print("=" * 80)
        
        # Count verified researchers
        verified_researchers = 0
        for user in researchers:
            kyc = db.query(KYCVerification).filter(
                KYCVerification.user_id == user.id,
                KYCVerification.status == 'approved'
            ).first()
            if kyc:
                verified_researchers += 1
        
        # Count verified organizations
        verified_organizations = 0
        for user in organizations:
            kyc = db.query(KYCVerification).filter(
                KYCVerification.user_id == user.id,
                KYCVerification.status == 'approved'
            ).first()
            if kyc:
                verified_organizations += 1
        
        print(f"\n✅ VERIFIED (KYC Approved):")
        print(f"   • Researchers: {verified_researchers} out of {len(researchers)}")
        print(f"   • Organizations: {verified_organizations} out of {len(organizations)}")
        
        print(f"\n📧 EMAIL VERIFIED:")
        email_verified_researchers = sum(1 for u in researchers if u.is_verified)
        email_verified_organizations = sum(1 for u in organizations if u.is_verified)
        print(f"   • Researchers: {email_verified_researchers} out of {len(researchers)}")
        print(f"   • Organizations: {email_verified_organizations} out of {len(organizations)}")
        
        print("\n" + "=" * 80)
        print("🔍 ANSWER TO YOUR QUESTION:")
        print("=" * 80)
        print(f"""
The counts shown are for ALL users in the database, not just verified ones:

• Total Users: {len(all_users)} (ALL users regardless of verification)
• Researchers: {len(researchers)} (ALL researcher accounts, verified or not)
• Organizations: {len(organizations)} (ALL organization user accounts, verified or not)
• Organization Records: {len(org_records)} (Separate organization profiles in 'organizations' table)

Verification Status:
• KYC Verified Researchers: {verified_researchers}/{len(researchers)}
• KYC Verified Organizations: {verified_organizations}/{len(organizations)}

The "N/A" issue in transactions means payments were processed for researchers
whose identity information (username, full_name) was not properly filled in,
NOT that they weren't verified. The backend fix now shows their email prefix
as a fallback instead of "N/A".
""")
        
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    check_all_users()
