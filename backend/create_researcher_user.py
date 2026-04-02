#!/usr/bin/env python3
"""Create a test researcher user."""

import sys
import os
from uuid import uuid4
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from src.core.database import SessionLocal
from src.domain.models.user import User
from src.domain.models.researcher import Researcher
from src.core.security import get_password_hash

def create_researcher():
    db = SessionLocal()
    try:
        # Check if user already exists
        existing = db.query(User).filter(User.email == "researcher@test.com").first()
        if existing:
            print("Researcher user already exists!")
            print(f"Email: researcher@test.com")
            print(f"Password: Password123!")
            return
        
        # Create user
        user = User(
            id=uuid4(),
            email="researcher@test.com",
            password_hash=get_password_hash("Password123!"),
            role="researcher",
            is_verified=True,
            created_at=datetime.utcnow()
        )
        db.add(user)
        db.flush()
        
        # Create researcher profile
        researcher = Researcher(
            id=uuid4(),
            user_id=user.id,
            bio="Test researcher for development",
            reputation_score=0,
            rank=0,
            total_earnings=0.0,
            created_at=datetime.utcnow()
        )
        db.add(researcher)
        
        db.commit()
        
        print("✓ Researcher user created successfully!")
        print(f"Email: researcher@test.com")
        print(f"Password: Password123!")
        print(f"Role: researcher")
        
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_researcher()
