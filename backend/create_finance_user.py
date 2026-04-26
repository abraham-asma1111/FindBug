#!/usr/bin/env python3
"""Create a finance officer user for testing"""

from src.core.database import SessionLocal
from src.domain.models.user import User
from src.domain.models.staff_profiles import FinanceOfficer
from src.core.security import get_password_hash
import uuid

def create_finance_user():
    db = SessionLocal()
    try:
        # Check if user exists
        existing = db.query(User).filter(User.email == 'finance@example.com').first()
        if existing:
            print(f"Finance user already exists: {existing.email}")
            return
        
        # Create user
        user = User(
            id=uuid.uuid4(),
            email='finance@example.com',
            hashed_password=get_password_hash('Password123!'),
            full_name='Finance Officer',
            role='finance_officer',
            is_active=True,
            is_verified=True
        )
        db.add(user)
        db.flush()
        
        # Create finance officer profile
        finance_profile = FinanceOfficer(
            id=uuid.uuid4(),
            user_id=user.id,
            department='Finance',
            permissions=['payment_approval', 'payout_processing', 'kyc_verification']
        )
        db.add(finance_profile)
        
        db.commit()
        print(f"✅ Finance user created successfully!")
        print(f"Email: finance@example.com")
        print(f"Password: Password123!")
        print(f"Role: finance_officer")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == '__main__':
    create_finance_user()
