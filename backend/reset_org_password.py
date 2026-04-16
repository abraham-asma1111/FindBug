#!/usr/bin/env python3
"""
Reset organization user password
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.domain.models.user import User
from src.core.security import get_password_hash

# Database connection
DATABASE_URL = "postgresql://bugbounty_user:changeme123@localhost:5432/bug_bounty_production"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def reset_password():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "org@example.com").first()
        if not user:
            print("❌ User not found")
            return
        
        user.password_hash = get_password_hash("password123")
        db.commit()
        
        print("✅ Password reset successfully")
        print(f"Email: org@example.com")
        print(f"Password: password123")
        
    finally:
        db.close()

if __name__ == "__main__":
    reset_password()
