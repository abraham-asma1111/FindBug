#!/usr/bin/env python3
"""
Check KYC verification data and pending payment methods in the database
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from src.core.config import settings

# Create database engine
engine = create_engine(settings.DATABASE_URL)
Session = sessionmaker(bind=engine)

def check_kyc_data():
    """Check KYC verification data"""
    print("\n" + "="*80)
    print("KYC VERIFICATION DATA")
    print("="*80)
    
    session = Session()
    try:
        # Check kyc_verifications table
        result = session.execute(text("""
            SELECT 
                k.id,
                k.user_id,
                u.email,
                r.username,
                k.email_verified,
                k.persona_verified,
                k.status,
                k.created_at,
                k.updated_at
            FROM kyc_verifications k
            JOIN users u ON k.user_id = u.id
            LEFT JOIN researchers r ON u.id = r.user_id
            ORDER BY k.created_at DESC
            LIMIT 20
        """))
        
        kyc_records = result.fetchall()
        
        if not kyc_records:
            print("\n❌ NO KYC RECORDS FOUND")
        else:
            print(f"\n✅ Found {len(kyc_records)} KYC records:\n")
            for record in kyc_records:
                print(f"ID: {record[0]}")
                print(f"  User: {record[3] or 'N/A'} ({record[2]})")
                print(f"  Email Verified: {record[4]}")
                print(f"  Persona Verified: {record[5]}")
                print(f"  Status: {record[6]}")
                print(f"  Created: {record[7]}")
                print(f"  Updated: {record[8]}")
                print("-" * 80)
        
        # Count by status
        result = session.execute(text("""
            SELECT status, COUNT(*) as count
            FROM kyc_verifications
            GROUP BY status
        """))
        
        status_counts = result.fetchall()
        if status_counts:
            print("\nKYC Status Summary:")
            for status, count in status_counts:
                print(f"  {status}: {count}")
        
    except Exception as e:
        print(f"\n❌ Error checking KYC data: {e}")
    finally:
        session.close()


def check_payment_methods():
    """Check payment methods data"""
    print("\n" + "="*80)
    print("PAYMENT METHODS DATA")
    print("="*80)
    
    session = Session()
    try:
        # Check payment_methods table
        result = session.execute(text("""
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
                pm.created_at
            FROM payment_methods pm
            JOIN users u ON pm.user_id = u.id
            LEFT JOIN researchers r ON u.id = r.user_id
            ORDER BY pm.created_at DESC
            LIMIT 20
        """))
        
        payment_methods = result.fetchall()
        
        if not payment_methods:
            print("\n❌ NO PAYMENT METHODS FOUND")
        else:
            print(f"\n✅ Found {len(payment_methods)} payment methods:\n")
            for pm in payment_methods:
                print(f"ID: {pm[0]}")
                print(f"  User: {pm[3] or 'N/A'} ({pm[2]})")
                print(f"  Method Type: {pm[4]}")
                print(f"  Account Name: {pm[5]}")
                print(f"  Account Number: {pm[6]}")
                if pm[7]:
                    print(f"  Bank: {pm[7]}")
                if pm[8]:
                    print(f"  Phone: {pm[8]}")
                print(f"  Verified: {'✓ YES' if pm[9] else '✗ NO (PENDING)'}")
                print(f"  Created: {pm[10]}")
                print("-" * 80)
        
        # Count by verification status
        result = session.execute(text("""
            SELECT 
                CASE WHEN is_verified THEN 'Verified' ELSE 'Pending' END as status,
                COUNT(*) as count
            FROM payment_methods
            GROUP BY is_verified
        """))
        
        verification_counts = result.fetchall()
        if verification_counts:
            print("\nPayment Method Verification Summary:")
            for status, count in verification_counts:
                print(f"  {status}: {count}")
        
        # Show pending payment methods specifically
        result = session.execute(text("""
            SELECT COUNT(*) FROM payment_methods WHERE is_verified = FALSE
        """))
        pending_count = result.scalar()
        print(f"\n🔔 PENDING APPROVAL: {pending_count} payment methods")
        
    except Exception as e:
        print(f"\n❌ Error checking payment methods: {e}")
    finally:
        session.close()


def check_researchers_with_kyc():
    """Check researchers and their KYC status"""
    print("\n" + "="*80)
    print("RESEARCHERS WITH KYC STATUS")
    print("="*80)
    
    session = Session()
    try:
        result = session.execute(text("""
            SELECT 
                u.id,
                u.email,
                r.username,
                k.email_verified,
                k.persona_verified,
                k.status as kyc_status,
                COUNT(pm.id) as payment_methods_count,
                COUNT(CASE WHEN pm.is_verified = FALSE THEN 1 END) as pending_payment_methods
            FROM users u
            JOIN researchers r ON u.id = r.user_id
            LEFT JOIN kyc_verifications k ON u.id = k.user_id
            LEFT JOIN payment_methods pm ON u.id = pm.user_id
            GROUP BY u.id, u.email, r.username, k.email_verified, k.persona_verified, k.status
            ORDER BY u.created_at DESC
            LIMIT 20
        """))
        
        researchers = result.fetchall()
        
        if not researchers:
            print("\n❌ NO RESEARCHERS FOUND")
        else:
            print(f"\n✅ Found {len(researchers)} researchers:\n")
            for res in researchers:
                print(f"User ID: {res[0]}")
                print(f"  Email: {res[1]}")
                print(f"  Username: {res[2]}")
                print(f"  KYC Status: {res[5] or 'NOT STARTED'}")
                print(f"  Email Verified: {res[3] if res[3] is not None else 'N/A'}")
                print(f"  Persona Verified: {res[4] if res[4] is not None else 'N/A'}")
                print(f"  Payment Methods: {res[6]} total, {res[7]} pending approval")
                print("-" * 80)
        
    except Exception as e:
        print(f"\n❌ Error checking researchers: {e}")
    finally:
        session.close()


def main():
    print("\n" + "="*80)
    print("DATABASE CHECK: KYC & PAYMENT METHODS")
    print("="*80)
    print(f"Database: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'local'}")
    
    check_kyc_data()
    check_payment_methods()
    check_researchers_with_kyc()
    
    print("\n" + "="*80)
    print("CHECK COMPLETE")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
