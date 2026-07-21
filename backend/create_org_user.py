#!/usr/bin/env python3
"""
Create an organization user for testing
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.domain.models.user import User, UserRole
from src.domain.models.organization import Organization
from src.core.security import get_password_hash
import uuid

# Database connection
DATABASE_URL = "postgresql://bugbounty_user:changeme123@localhost:5432/bug_bounty_production"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def create_org_user():
    print("\n" + "="*60)
    print("  CREATING ORGANIZATION USER")
    print("="*60 + "\n")
    
    db = SessionLocal()
    try:
        # Check if user exists
        existing_user = db.query(User).filter(User.email == "org@example.com").first()
        if existing_user:
            print(f"✅ Organization user already exists: {existing_user.email}")
            print(f"   User ID: {existing_user.id}")
            print(f"   Role: {existing_user.role}")
            
            # Check if organization profile exists
            if existing_user.organization:
                print(f"   Organization ID: {existing_user.organization.id}")
                print(f"   Company Name: {existing_user.organization.company_name}")
            else:
                print("   ⚠️  No organization profile found, creating...")
                org = Organization(
                    id=uuid.uuid4(),
                    user_id=existing_user.id,
                    company_name="Test Organization",
                    website="https://example.com",
                    industry="Technology"
                )
                db.add(org)
                db.commit()
                print(f"   ✅ Created organization profile: {org.id}")
            return
        
        # Create user
        user = User(
            id=uuid.uuid4(),
            email="org@example.com",
            password_hash=get_password_hash("password123"),
            role=UserRole.ORGANIZATION,
            is_verified=True,
            is_active=True
        )
        db.add(user)
        db.flush()
        
        print(f"✅ Created user: {user.email}")
        print(f"   User ID: {user.id}")
        print(f"   Role: {user.role}")
        
        # Create organization profile
        org = Organization(
            id=uuid.uuid4(),
            user_id=user.id,
            company_name="Test Organization",
            website="https://example.com",
            industry="Technology"
        )
        db.add(org)
        db.commit()
        
        print(f"✅ Created organization profile: {org.id}")
        print(f"   Company Name: {org.company_name}")
        
        print("\n" + "="*60)
        print("  SUCCESS!")
        print("="*60)
        print("\nLogin credentials:")
        print("  Email: org@example.com")
        print("  Password: password123")
        print("="*60 + "\n")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    create_org_user()
