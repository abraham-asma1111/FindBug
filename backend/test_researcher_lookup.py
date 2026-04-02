#!/usr/bin/env python3
"""Test researcher lookup."""
import sys
sys.path.insert(0, '/home/abraham/Desktop/Final-year-project/backend')

from sqlalchemy.orm import Session
from src.core.database import SessionLocal
from src.domain.models.user import User
from src.domain.models.researcher import Researcher

db = SessionLocal()

# Find researcher user
user = db.query(User).filter(User.email == "researcher@test.com").first()
if not user:
    print("User not found")
    sys.exit(1)

print(f"User ID: {user.id}")
print(f"User Role: {user.role}")

# Try to get researcher by user_id
researcher = db.query(Researcher).filter(Researcher.user_id == user.id).first()
if researcher:
    print(f"✓ Researcher found: {researcher.id}")
else:
    print("✗ Researcher not found by user_id")

# Check if user has researcher relationship
if hasattr(user, 'researcher') and user.researcher:
    print(f"✓ User.researcher exists: {user.researcher.id}")
else:
    print("✗ User.researcher not loaded or doesn't exist")

db.close()
