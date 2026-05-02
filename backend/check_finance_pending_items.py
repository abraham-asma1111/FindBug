#!/usr/bin/env python3
"""
Quick check for pending items that Finance Officers need to review
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from src.core.config import settings

engine = create_engine(settings.DATABASE_URL)
Session = sessionmaker(bind=engine)

def main():
    print("\n" + "="*80)
    print("FINANCE OFFICER - PENDING ITEMS FOR REVIEW")
    print("="*80)
    
    session = Session()
    
    try:
        # 1. Pending Payment Methods
        print("\n📋 PENDING PAYMENT METHODS:")
        print("-" * 80)
        result = session.execute(text("""
            SELECT 
                pm.id,
                u.email,
                r.username,
                pm.method_type,
                pm.account_name,
                pm.account_number,
                pm.bank_name,
                pm.phone_number,
                pm.created_at
            FROM payment_methods pm
            JOIN users u ON pm.user_id = u.id
            LEFT JOIN researchers r ON u.id = r.user_id
            WHERE pm.is_verified = FALSE
            ORDER BY pm.created_at DESC
        """))
        
        payment_methods = result.fetchall()
        if payment_methods:
            for i, pm in enumerate(payment_methods, 1):
                print(f"\n{i}. Payment Method ID: {pm[0]}")
                print(f"   Researcher: {pm[2] or 'N/A'} ({pm[1]})")
                print(f"   Type: {pm[3]}")
                print(f"   Account: {pm[4]} - {pm[5]}")
                if pm[6]:
                    print(f"   Bank: {pm[6]}")
                if pm[7]:
                    print(f"   Phone: {pm[7]}")
                print(f"   Submitted: {pm[8]}")
        else:
            print("   ✓ No pending payment methods")
        
        # 2. KYC Verifications
        print("\n\n📋 KYC VERIFICATIONS:")
        print("-" * 80)
        result = session.execute(text("""
            SELECT 
                k.id,
                u.email,
                r.username,
                k.status,
                k.email_verified,
                k.persona_verified_at,
                k.created_at
            FROM kyc_verifications k
            JOIN users u ON k.user_id = u.id
            LEFT JOIN researchers r ON u.id = r.user_id
            ORDER BY k.created_at DESC
            LIMIT 20
        """))
        
        kyc_records = result.fetchall()
        if kyc_records:
            pending_count = sum(1 for k in kyc_records if k[3] == 'pending')
            print(f"   Total: {len(kyc_records)} records, {pending_count} pending")
            
            for i, k in enumerate(kyc_records, 1):
                if k[3] == 'pending':  # Only show pending
                    print(f"\n{i}. KYC ID: {k[0]}")
                    print(f"   Researcher: {k[2] or 'N/A'} ({k[1]})")
                    print(f"   Status: {k[3]}")
                    print(f"   Email Verified: {k[4]}")
                    print(f"   Persona Verified: {'Yes' if k[5] else 'No'}")
                    print(f"   Submitted: {k[6]}")
        else:
            print("   ✓ No KYC records found")
        
        # 3. Summary
        print("\n\n" + "="*80)
        print("SUMMARY")
        print("="*80)
        print(f"✓ Pending Payment Methods: {len(payment_methods)}")
        print(f"✓ Total KYC Records: {len(kyc_records)}")
        if kyc_records:
            pending_kyc = sum(1 for k in kyc_records if k[3] == 'pending')
            print(f"✓ Pending KYC Verifications: {pending_kyc}")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    main()
