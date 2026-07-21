#!/usr/bin/env python3
"""Check researcher profile."""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from src.core.database import SessionLocal
from src.domain.models.user import User
from src.domain.models.researcher import Researcher

def check_researcher():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "researcher@test.com").first()
        if not user:
            print("❌ User not found")
            return
        
        print(f"✓ User found: {user.email}")
        print(f"  ID: {user.id}")
        print(f"  Role: {user.role}")
        print(f"  Verified: {user.is_verified}")
        
        researcher = db.query(Researcher).filter(Researcher.user_id == user.id).first()
        if not researcher:
            print("❌ Researcher profile not found")
            return
        
        print(f"✓ Researcher profile found")
        print(f"  ID: {researcher.id}")
        print(f"  User ID: {researcher.user_id}")
        
    finally:
        db.close()

if __name__ == "__main__":
    check_researcher()
