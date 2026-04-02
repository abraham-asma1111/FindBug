#!/usr/bin/env python3
"""
Quick script to create an organization user for testing
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy.orm import Session
from src.core.database import SessionLocal
from src.domain.models.user import User
from src.domain.models.organization import Organization
from src.core.security import get_password_hash
import uuid

def create_org_user():
    db: Session = SessionLocal()
    
    try:
        # Check if user already exists
        existing = db.query(User).filter(User.email == "org@test.com").first()
        if existing:
            print("✅ Organization user already exists!")
            print(f"Email: org@test.com")
            print(f"Password: Password123!")
            print(f"Role: organization")
            return
        
        # Create user
        user = User(
            id=uuid.uuid4(),
            email="org@test.com",
            password_hash=get_password_hash("Password123!"),
            role="organization",
            is_verified=True,
            is_active=True
        )
        db.add(user)
        db.flush()
        
        # Create organization profile
        org = Organization(
            id=uuid.uuid4(),
            user_id=user.id,
            company_name="Test Company",
            industry="Technology",
            website="https://testcompany.com",
            subscription_type="enterprise",
            domain_verified=True,
            verification_status="verified"
        )
        db.add(org)
        
        db.commit()
        
        print("✅ Organization user created successfully!")
        print(f"\nLogin Credentials:")
        print(f"Email: org@test.com")
        print(f"Password: Password123!")
        print(f"Role: organization")
        print(f"\nGo to: http://localhost:3000/auth/login")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_org_user()
