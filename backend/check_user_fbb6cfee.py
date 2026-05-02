#!/usr/bin/env python3
"""Check user fbb6cfee-03f4-4784-b1a1-623868f69941"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy.orm import Session
from src.core.database import SessionLocal
from src.domain.models.user import User
from uuid import UUID

def check_user():
    db: Session = SessionLocal()
    
    try:
        user_id = "fbb6cfee-03f4-4784-b1a1-623868f69941"
        user = db.query(User).filter(User.id == UUID(user_id)).first()
        
        if not user:
            print(f"❌ User {user_id} not found!")
            return
        
        print("=" * 80)
        print("USER INFO")
        print("=" * 80)
        print(f"User ID: {user.id}")
        print(f"Email: {user.email}")
        print(f"Role: {user.role}")
        print(f"Created: {user.created_at}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_user()
