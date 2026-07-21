#!/usr/bin/env python3
"""
Diagnostic script to check KYC status mismatches between:
- Database values
- Backend API responses
- Frontend expectations
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.domain.models.kyc import KYCVerification
from src.domain.models.user import User
from datetime import datetime

# Database connection
DATABASE_URL = "postgresql://bugbounty_user:bugbounty_pass@localhost:5432/bugbounty_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def check_status_mismatch():
    """Check for status mismatches in KYC records"""
    db = SessionLocal()
    
    try:
        print("=" * 80)
        print("KYC STATUS MISMATCH DIAGNOSTIC")
        print("=" * 80)
        print()
        
        # Get all KYC records
        kyc_records = db.query(KYCVerification).join(User).all()
        
        if not kyc_records:
            print("❌ No KYC records found in database")
            return
        
        print(f"✅ Found {len(kyc_records)} KYC record(s)\n")
        
        for idx, kyc in enumerate(kyc_records, 1):
            user = kyc.user
            print(f"{'=' * 80}")
            print(f"RECORD #{idx}")
            print(f"{'=' * 80}")
            print(f"User ID:           {kyc.user_id}")
            print(f"User Email:        {user.email if user else 'N/A'}")
            print(f"User Role:         {user.role if user else 'N/A'}")
            print()
            
            # Database values
            print("📊 DATABASE VALUES:")
            print(f"  status:                    {kyc.status}")
            print(f"  persona_status:            {kyc.persona_status}")
            print(f"  persona_inquiry_id:        {kyc.persona_inquiry_id}")
            print(f"  phone_verified:            {kyc.phone_verified}")
            print(f"  phone_number:              {kyc.phone_number}")
            print(f"  verified_at:               {kyc.verified_at}")
            print(f"  persona_verified_at:       {kyc.persona_verified_at}")
            print()
            
            # Backend logic checks
            print("🔧 BACKEND LOGIC CHECKS:")
            
            # Check 1: Persona approval status
            persona_approved_old = kyc.status == "approved" and kyc.persona_status == "completed"
            persona_approved_new = kyc.status == "approved" and kyc.persona_status in ["completed", "approved"]
            
            print(f"  Persona approved (OLD logic): {persona_approved_old}")
            print(f"  Persona approved (NEW logic): {persona_approved_new}")
            
            if persona_approved_old != persona_approved_new:
                print(f"  ⚠️  MISMATCH: Old logic would {'APPROVE' if persona_approved_old else 'REJECT'}")
                print(f"              New logic would {'APPROVE' if persona_approved_new else 'REJECT'}")
            
            # Check 2: Can verify phone
            can_verify_phone = kyc.status == "approved" and not kyc.phone_verified
            print(f"  Can verify phone:          {can_verify_phone}")
            
            # Check 3: Fully verified
            fully_verified = (kyc.status == "approved" and 
                            kyc.persona_status in ["completed", "approved"] and 
                            kyc.phone_verified)
            print(f"  Fully verified:            {fully_verified}")
            print()
            
            # Frontend expectations
            print("🎨 FRONTEND EXPECTATIONS:")
            print(f"  Step 1 (Persona) status:   {'✅ COMPLETE' if kyc.persona_status in ['completed', 'approved'] else '❌ INCOMPLETE'}")
            print(f"  Step 2 (SMS) unlocked:     {'✅ YES' if can_verify_phone else '❌ NO'}")
            print(f"  Step 2 (SMS) status:       {'✅ COMPLETE' if kyc.phone_verified else '❌ INCOMPLETE'}")
            print()
            
            # API response simulation
            print("📡 API RESPONSE (/kyc/persona/status):")
            api_response = {
                "status": kyc.status,
                "persona_status": kyc.persona_status,
                "persona_inquiry_id": kyc.persona_inquiry_id,
                "phone_verified": kyc.phone_verified or False,
                "phone_number": kyc.phone_number,
                "can_verify_phone": can_verify_phone
            }
            for key, value in api_response.items():
                print(f"  {key:25} {value}")
            print()
            
            # Issue detection
            print("🔍 ISSUE DETECTION:")
            issues = []
            
            # Issue 1: Persona status is "approved" but kyc.status is not "approved"
            if kyc.persona_status == "approved" and kyc.status != "approved":
                issues.append("❌ Persona status is 'approved' but KYC status is not 'approved'")
            
            # Issue 2: Persona status is "completed" but kyc.status is not "approved"
            if kyc.persona_status == "completed" and kyc.status != "approved":
                issues.append("❌ Persona status is 'completed' but KYC status is not 'approved'")
            
            # Issue 3: KYC approved but no verified_at timestamp
            if kyc.status == "approved" and not kyc.verified_at:
                issues.append("⚠️  KYC approved but verified_at is NULL")
            
            # Issue 4: Phone verified but no phone_verified_at timestamp
            if kyc.phone_verified and not kyc.phone_verified_at:
                issues.append("⚠️  Phone verified but phone_verified_at is NULL")
            
            # Issue 5: can_verify_phone is False when it should be True
            if kyc.status == "approved" and kyc.persona_status in ["completed", "approved"] and not kyc.phone_verified:
                if not can_verify_phone:
                    issues.append("❌ SMS verification should be unlocked but can_verify_phone is False")
            
            if issues:
                for issue in issues:
                    print(f"  {issue}")
            else:
                print("  ✅ No issues detected")
            
            print()
        
        print("=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print()
        print("Status values that backend accepts:")
        print("  - Persona approved: 'approved' OR 'completed'")
        print("  - KYC approved:     'approved'")
        print("  - Phone verified:   phone_verified = True")
        print()
        print("Frontend unlock conditions:")
        print("  - Step 1 complete:  persona_status in ['approved', 'completed']")
        print("  - Step 2 unlocked:  status == 'approved' AND phone_verified == False")
        print("  - Step 2 complete:  phone_verified == True")
        print("  - Fully verified:   status == 'approved' AND persona_status in ['approved', 'completed'] AND phone_verified == True")
        print()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_status_mismatch()
