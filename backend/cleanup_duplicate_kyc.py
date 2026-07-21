"""
Clean up duplicate KYC records - keep only the latest one per user
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from src.domain.models.kyc import KYCVerification
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

print("=" * 80)
print("CLEANING UP DUPLICATE KYC RECORDS")
print("=" * 80)

# Find users with multiple KYC records
duplicate_kyc = db.query(
    KYCVerification.user_id,
    func.count(KYCVerification.id).label('count')
).group_by(
    KYCVerification.user_id
).having(
    func.count(KYCVerification.id) > 1
).all()

if not duplicate_kyc:
    print("\n✓ No duplicate KYC records found. Database is clean!")
    db.close()
    sys.exit(0)

print(f"\nFound {len(duplicate_kyc)} users with multiple KYC records\n")

total_deleted = 0

for user_id, count in duplicate_kyc:
    print(f"Processing User ID: {user_id} ({count} records)")
    
    # Get all KYC records for this user, ordered by created_at DESC (newest first)
    kyc_records = db.query(KYCVerification).filter(
        KYCVerification.user_id == user_id
    ).order_by(
        KYCVerification.created_at.desc()
    ).all()
    
    # Keep the first one (newest), delete the rest
    latest_kyc = kyc_records[0]
    old_records = kyc_records[1:]
    
    print(f"  ✓ Keeping latest record (ID: {latest_kyc.id}):")
    print(f"    - Status: {latest_kyc.status}")
    print(f"    - Email Verified: {latest_kyc.email_verified}")
    print(f"    - Persona Verified: {latest_kyc.persona_verified_at is not None}")
    print(f"    - Created: {latest_kyc.created_at}")
    
    print(f"  ✗ Deleting {len(old_records)} old record(s):")
    for old_kyc in old_records:
        print(f"    - ID: {old_kyc.id}, Status: {old_kyc.status}, Created: {old_kyc.created_at}")
        db.delete(old_kyc)
        total_deleted += 1
    
    print()

# Commit the changes
try:
    db.commit()
    print("=" * 80)
    print(f"✓ Successfully deleted {total_deleted} duplicate KYC record(s)")
    print("=" * 80)
except Exception as e:
    db.rollback()
    print(f"✗ Error during cleanup: {str(e)}")
    print("Changes have been rolled back")
finally:
    db.close()
