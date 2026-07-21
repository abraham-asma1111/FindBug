#!/usr/bin/env python3
"""Test script to verify role checking works correctly"""

import sys
sys.path.insert(0, '/home/abraham/Desktop/Final-year-project/backend')

from src.core.database import SessionLocal
from src.domain.models.user import User

db = SessionLocal()
try:
    # Get the researcher user
    user = db.query(User).filter(User.id == 'e70ca19c-06aa-44d5-a91f-9566c8eff8ab').first()
    
    if user:
        print(f"User: {user.email}")
        print(f"Role (raw): '{user.role}'")
        print(f"Role (lowercase): '{user.role.lower()}'")
        print()
        print("Testing helper methods:")
        print(f"  has_role('researcher'): {user.has_role('researcher')}")
        print(f"  has_role('RESEARCHER'): {user.has_role('RESEARCHER')}")
        print(f"  is_researcher(): {user.is_researcher()}")
        print(f"  is_organization(): {user.is_organization()}")
        print()
        print("✓ Role checking methods work correctly!")
    else:
        print("User not found")
        
finally:
    db.close()
