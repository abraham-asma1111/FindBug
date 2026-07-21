import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from src.core.database import SessionLocal
from src.domain.models.kyc import KYCVerification

db: Session = SessionLocal()

try:
    pending_kyc = db.query(KYCVerification).filter(
        KYCVerification.status == 'pending'
    ).all()
    
    print(f"Found {len(pending_kyc)} pending KYC records")
    
    for kyc in pending_kyc:
        print(f"Deleting KYC for user: {kyc.user_id}")
        db.delete(kyc)
    
    db.commit()
    print("\n✅ All pending KYC records deleted")
finally:
    db.close()
