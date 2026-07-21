import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from src.core.database import SessionLocal
from src.domain.models.kyc import KYCVerification

user_id = "6a2c85a9-e707-4aec-b480-9d4fe5b69cba"

db: Session = SessionLocal()

try:
    kyc = db.query(KYCVerification).filter(
        KYCVerification.user_id == user_id
    ).first()
    
    if kyc:
        print(f"Found KYC record:")
        print(f"  Status: {kyc.status}")
        print(f"  Persona Inquiry ID: {kyc.persona_inquiry_id}")
        print(f"  Persona Status: {kyc.persona_status}")
        
        db.delete(kyc)
        db.commit()
        print(f"\n✅ KYC record deleted for user {user_id}")
    else:
        print(f"No KYC record found for user {user_id}")
finally:
    db.close()
