#!/usr/bin/env python3
"""
Delete current KYC record that's stuck in pending state
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from src.core.database import SessionLocal
from src.domain.models.kyc import KYCVerification

db: Session = SessionLocal()

try:
    # Delete the specific inquiry that's stuck
    stuck_inquiry_id = "inq_AQvunKjCsd3niZx9EJ3hM9FwajAWMy"
    
    kyc = db.query(KYCVerification).filter(
        KYCVerification.persona_inquiry_id == stuck_inquiry_id
    ).first()
    
    if kyc:
        print(f"Found stuck KYC record:")
        print(f"  User ID: {kyc.user_id}")
        print(f"  Status: {kyc.status}")
        print(f"  Persona Status: {kyc.persona_status}")
        print(f"  Inquiry ID: {kyc.persona_inquiry_id}")
        
        db.delete(kyc)
        db.commit()
        print("\n✅ Stuck KYC record deleted")
    else:
        print(f"No KYC record found with inquiry_id: {stuck_inquiry_id}")
        
        # Show all KYC records
        all_kyc = db.query(KYCVerification).all()
        print(f"\nFound {len(all_kyc)} total KYC records:")
        for k in all_kyc:
            print(f"  User: {k.user_id}, Status: {k.status}, Persona Status: {k.persona_status}, Inquiry: {k.persona_inquiry_id}")
            
finally:
    db.close()
