#!/usr/bin/env python3
"""
Check Finance Officer Data - Payments, Payouts, and KYC Verifications
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import create_engine, text
from src.core.config import settings

def main():
    print("=" * 80)
    print("FINANCE OFFICER DATA CHECK")
    print("=" * 80)
    print(f"Database: {settings.DATABASE_URL}\n")
    
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        # Check Payment Methods (Pending Approval)
        print("=" * 80)
        print("1. PAYMENT METHODS (Pending Approval)")
        print("=" * 80)
        
        result = conn.execute(text("""
            SELECT 
                pm.id,
                pm.user_id,
                u.email,
                r.username,
                pm.method_type,
                pm.account_name,
                pm.account_number,
                pm.bank_name,
                pm.phone_number,
                pm.is_verified,
                pm.created_at,
                k.email_verified,
                k.persona_verified_at,
                k.status as kyc_status
            FROM payment_methods pm
            JOIN users u ON pm.user_id = u.id
            LEFT JOIN researchers r ON u.id = r.user_id
            LEFT JOIN kyc_verifications k ON u.id = k.user_id
            WHERE pm.is_verified = FALSE
            ORDER BY pm.created_at DESC
        """))
        
        payment_methods = result.fetchall()
        
        if payment_methods:
            print(f"\n✅ Found {len(payment_methods)} pending payment methods:\n")
            for pm in payment_methods:
                print(f"ID: {pm[0]}")
                print(f"  Researcher: {pm[3] or 'N/A'} ({pm[2]})")
                print(f"  Method: {pm[4]}")
                print(f"  Account Name: {pm[5]}")
                print(f"  Account Number: {pm[6]}")
                if pm[7]:
                    print(f"  Bank: {pm[7]}")
                if pm[8]:
                    print(f"  Phone: {pm[8]}")
                print(f"  KYC Status:")
                print(f"    - Email Verified: {'✓' if pm[11] else '✗'}")
                print(f"    - Persona Verified: {'✓' if pm[12] else '✗'}")
                print(f"    - Overall Status: {pm[13] or 'N/A'}")
                print(f"  Created: {pm[10]}")
                print("-" * 80)
        else:
            print("\n❌ No pending payment methods found")
        
        # Check KYC Verifications
        print("\n" + "=" * 80)
        print("2. KYC VERIFICATIONS")
        print("=" * 80)
        
        result = conn.execute(text("""
            SELECT 
                k.id,
                k.user_id,
                u.email,
                r.username,
                k.status,
                k.email_verified,
                k.persona_verified_at,
                k.persona_inquiry_id,
                k.created_at,
                k.updated_at
            FROM kyc_verifications k
            JOIN users u ON k.user_id = u.id
            LEFT JOIN researchers r ON u.id = r.user_id
            ORDER BY k.created_at DESC
            LIMIT 20
        """))
        
        kyc_verifications = result.fetchall()
        
        if kyc_verifications:
            print(f"\n✅ Found {len(kyc_verifications)} KYC verifications:\n")
            
            pending = [k for k in kyc_verifications if k[4] == 'pending']
            approved = [k for k in kyc_verifications if k[4] == 'approved']
            rejected = [k for k in kyc_verifications if k[4] == 'rejected']
            
            print(f"Status Summary:")
            print(f"  - Pending: {len(pending)}")
            print(f"  - Approved: {len(approved)}")
            print(f"  - Rejected: {len(rejected)}")
            print()
            
            for k in kyc_verifications[:10]:  # Show first 10
                print(f"ID: {k[0]}")
                print(f"  Researcher: {k[3] or 'N/A'} ({k[2]})")
                print(f"  Status: {k[4]}")
                print(f"  Email Verified: {'✓' if k[5] else '✗'}")
                print(f"  Persona Verified: {'✓' if k[6] else '✗'}")
                if k[7]:
                    print(f"  Persona Inquiry ID: {k[7]}")
                print(f"  Created: {k[8]}")
                print("-" * 80)
        else:
            print("\n❌ No KYC verifications found")
        
        # Check Bounty Payments
        print("\n" + "=" * 80)
        print("3. BOUNTY PAYMENTS")
        print("=" * 80)
        
        result = conn.execute(text("""
            SELECT 
                bp.payment_id,
                bp.transaction_id,
                bp.report_id,
                bp.researcher_id,
                r.username,
                bp.researcher_amount,
                bp.commission_amount,
                bp.total_amount,
                bp.status,
                bp.created_at,
                bp.approved_at
            FROM bounty_payments bp
            LEFT JOIN researchers r ON bp.researcher_id = r.id
            ORDER BY bp.created_at DESC
            LIMIT 20
        """))
        
        payments = result.fetchall()
        
        if payments:
            print(f"\n✅ Found {len(payments)} bounty payments:\n")
            
            pending = [p for p in payments if p[8] == 'pending']
            approved = [p for p in payments if p[8] == 'approved']
            completed = [p for p in payments if p[8] == 'completed']
            
            print(f"Status Summary:")
            print(f"  - Pending: {len(pending)}")
            print(f"  - Approved: {len(approved)}")
            print(f"  - Completed: {len(completed)}")
            print()
            
            for p in payments[:5]:  # Show first 5
                print(f"Payment ID: {p[0]}")
                print(f"  Researcher: {p[4] or 'N/A'}")
                print(f"  Amount: {p[5]} ETB")
                print(f"  Commission: {p[6]} ETB")
                print(f"  Total: {p[7]} ETB")
                print(f"  Status: {p[8]}")
                print(f"  Created: {p[9]}")
                if p[10]:
                    print(f"  Approved: {p[10]}")
                print("-" * 80)
        else:
            print("\n❌ No bounty payments found")
        
        # Check Payout Requests
        print("\n" + "=" * 80)
        print("4. PAYOUT REQUESTS")
        print("=" * 80)
        
        result = conn.execute(text("""
            SELECT 
                pr.id,
                pr.researcher_id,
                r.username,
                pr.amount,
                pr.payment_method,
                pr.status,
                pr.created_at,
                pr.processed_at
            FROM payout_requests pr
            LEFT JOIN researchers r ON pr.researcher_id = r.id
            ORDER BY pr.created_at DESC
            LIMIT 20
        """))
        
        payouts = result.fetchall()
        
        if payouts:
            print(f"\n✅ Found {len(payouts)} payout requests:\n")
            
            requested = [p for p in payouts if p[5] == 'requested']
            processing = [p for p in payouts if p[5] == 'processing']
            completed = [p for p in payouts if p[5] == 'completed']
            
            print(f"Status Summary:")
            print(f"  - Requested: {len(requested)}")
            print(f"  - Processing: {len(processing)}")
            print(f"  - Completed: {len(completed)}")
            print()
            
            for p in payouts[:5]:  # Show first 5
                print(f"Payout ID: {p[0]}")
                print(f"  Researcher: {p[2] or 'N/A'}")
                print(f"  Amount: {p[3]} ETB")
                print(f"  Method: {p[4]}")
                print(f"  Status: {p[5]}")
                print(f"  Created: {p[6]}")
                if p[7]:
                    print(f"  Processed: {p[7]}")
                print("-" * 80)
        else:
            print("\n❌ No payout requests found")
    
    print("\n" + "=" * 80)
    print("CHECK COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()
