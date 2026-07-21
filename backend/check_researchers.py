#!/usr/bin/env python3
"""
Check and list all researchers in the database
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.domain.models.researcher import Researcher
from src.domain.models.user import User

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://bountyuser:bountypass@localhost:5432/bountydb")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def check_researchers():
    db = SessionLocal()
    try:
        print("\n" + "="*60)
        print("  CHECKING RESEARCHERS IN DATABASE")
        print("="*60 + "\n")
        
        # Get all researchers
        researchers = db.query(Researcher).join(User).all()
        
        if not researchers:
            print("❌ NO RESEARCHERS FOUND IN DATABASE!")
            print("\nTo create test researchers, run:")
            print("  python backend/create_researcher_user.py")
            return
        
        print(f"✅ Found {len(researchers)} researcher(s):\n")
        
        for idx, researcher in enumerate(researchers, 1):
            # Handle both direct attribute and relationship access
            username = getattr(researcher.user, 'username', None) or researcher.user.email.split('@')[0]
            email = getattr(researcher.user, 'email', 'N/A')
            
            print(f"{idx}. {username}")
            print(f"   Email: {email}")
            print(f"   Reputation: {researcher.reputation_score}")
            print(f"   Total Reports: {researcher.total_reports}")
            print(f"   Verified Reports: {researcher.verified_reports}")
            print(f"   Active: {researcher.is_active}")
            print(f"   ID: {researcher.id}")
            print()
        
        print("="*60)
        print(f"Total: {len(researchers)} researchers")
        print("="*60 + "\n")
        
    finally:
        db.close()

if __name__ == "__main__":
    check_researchers()
