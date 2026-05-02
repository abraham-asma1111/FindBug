"""
Check for duplicate or inconsistent KYC records
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from src.domain.models.kyc import KYCVerification
from src.domain.models.user import User
from src.domain.models.payment_extended import PaymentMethod
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

print("=" * 80)
print("CHECKING FOR DUPLICATE KYC RECORDS")
print("=" * 80)

# Check for users with multiple KYC records
duplicate_kyc = db.query(
    KYCVerification.user_id,
    func.count(KYCVerification.id).label('count')
).group_by(
    KYCVerification.user_id
).having(
    func.count(KYCVerification.id) > 1
).all()

if duplicate_kyc:
    print(f"\n⚠️  Found {len(duplicate_kyc)} users with multiple KYC records:")
    for user_id, count in duplicate_kyc:
        print(f"  User ID: {user_id} has {count} KYC records")
        
        # Show details of each KYC record
        kyc_records = db.query(KYCVerification).filter(
            KYCVerification.user_id == user_id
        ).all()
        
        for i, kyc in enumerate(kyc_records, 1):
            print(f"    Record {i}:")
            print(f"      - Status: {kyc.status}")
            print(f"      - Email Verified: {kyc.email_verified}")
            print(f"      - Persona Verified At: {kyc.persona_verified_at}")
            print(f"      - Created At: {kyc.created_at}")
else:
    print("\n✓ No duplicate KYC records found")

print("\n" + "=" * 80)
print("CHECKING PAYMENT METHODS WITH KYC STATUS")
print("=" * 80)

# Get all pending payment methods with their KYC status
results = db.query(
    PaymentMethod,
    User.email,
    KYCVerification.email_verified,
    KYCVerification.persona_verified_at
).join(
    User, PaymentMethod.user_id == User.id
).outerjoin(
    KYCVerification, User.id == KYCVerification.user_id
).filter(
    PaymentMethod.is_verified == False
).all()

print(f"\nFound {len(results)} pending payment methods:\n")

user_kyc_map = {}
for pm, email, email_verified, persona_verified_at in results:
    user_id = str(pm.user_id)
    
    # Track KYC status per user
    if user_id not in user_kyc_map:
        user_kyc_map[user_id] = {
            'email': email,
            'kyc_statuses': []
        }
    
    kyc_status = {
        'email_verified': email_verified,
        'persona_verified': persona_verified_at is not None,
        'payment_method_id': str(pm.id),
        'account': f"{pm.method_type} - {pm.account_number}"
    }
    user_kyc_map[user_id]['kyc_statuses'].append(kyc_status)

# Check for inconsistencies
print("User KYC Status Summary:")
for user_id, data in user_kyc_map.items():
    print(f"\n  User: {data['email']}")
    print(f"  User ID: {user_id}")
    
    # Check if all payment methods show the same KYC status
    statuses = data['kyc_statuses']
    if len(statuses) > 1:
        # Check for inconsistency
        first_status = (statuses[0]['email_verified'], statuses[0]['persona_verified'])
        inconsistent = any(
            (s['email_verified'], s['persona_verified']) != first_status
            for s in statuses[1:]
        )
        
        if inconsistent:
            print(f"  ⚠️  INCONSISTENT KYC STATUS across payment methods:")
            for s in statuses:
                verified_status = "✓ VERIFIED" if (s['email_verified'] and s['persona_verified']) else "PARTIAL"
                print(f"    - {s['account']}: {verified_status}")
                print(f"      Email: {s['email_verified']}, Persona: {s['persona_verified']}")
        else:
            verified_status = "✓ VERIFIED" if (first_status[0] and first_status[1]) else "PARTIAL"
            print(f"  ✓ Consistent KYC: {verified_status}")
            print(f"    Email Verified: {first_status[0]}, Persona Verified: {first_status[1]}")
    else:
        s = statuses[0]
        verified_status = "✓ VERIFIED" if (s['email_verified'] and s['persona_verified']) else "PARTIAL"
        print(f"  KYC Status: {verified_status}")
        print(f"    Email Verified: {s['email_verified']}, Persona Verified: {s['persona_verified']}")

db.close()
print("\n" + "=" * 80)
