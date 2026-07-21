#!/usr/bin/env python3
"""
List all organization users
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.domain.models.user import User, UserRole
from src.domain.models.organization import Organization

# Database connection
DATABASE_URL = "postgresql://bugbounty_user:changeme123@localhost:5432/bug_bounty_production"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def list_org_users():
    print("\n" + "="*60)
    print("  ALL ORGANIZATION USERS")
    print("="*60 + "\n")
    
    db = SessionLocal()
    try:
        # Get all organization users
        users = db.query(User).filter(User.role == UserRole.ORGANIZATION).all()
        
        if not users:
            print("❌ No organization users found!")
            return
        
        print(f"Found {len(users)} organization user(s):\n")
        
        for idx, user in enumerate(users, 1):
            print(f"{idx}. Email: {user.email}")
            print(f"   User ID: {user.id}")
            print(f"   Role: {user.role}")
            print(f"   Active: {user.is_active}")
            print(f"   Verified: {user.is_verified}")
            
            # Check organization profile
            if user.organization:
                print(f"   Organization ID: {user.organization.id}")
                print(f"   Company Name: {user.organization.company_name}")
            else:
                print(f"   ⚠️  No organization profile")
            print()
        
        print("="*60 + "\n")
        
    finally:
        db.close()

if __name__ == "__main__":
    list_org_users()
