import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from src.core.database import SessionLocal
from src.domain.models.kyc import KYCVerification

db: Session = SessionLocal()

try:
    all_kyc = db.query(KYCVerification).all()
    print(f"Total KYC records: {len(all_kyc)}\n")
    
    for kyc in all_kyc:
        print(f"User ID: {kyc.user_id}")
        print(f"Status: {kyc.status}")
        print(f"Persona Inquiry ID: {kyc.persona_inquiry_id}")
        print(f"Persona Status: {kyc.persona_status}")
        print("-" * 50)
finally:
    db.close()
