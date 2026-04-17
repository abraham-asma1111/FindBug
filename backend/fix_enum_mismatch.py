#!/usr/bin/env python3
"""
Fix the userrole enum mismatch between database and SQLAlchemy model.
The database has uppercase values (RESEARCHER, ORGANIZATION, etc.) from the initial migration,
but the model expects lowercase values (researcher, organization, etc.).
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Database connection
DATABASE_URL = "postgresql://bugbounty_user:changeme123@localhost:5432/bug_bounty_production"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def check_current_enum_values():
    """Check what values exist in the userrole enum"""
    db = SessionLocal()
    try:
        result = db.execute(text("""
            SELECT e.enumlabel 
            FROM pg_enum e
            JOIN pg_type t ON e.enumtypid = t.oid
            WHERE t.typname = 'userrole'
            ORDER BY e.enumsortorder;
        """))
        values = [row[0] for row in result]
        print(f"Current userrole enum values: {values}")
        return values
    finally:
        db.close()

def check_user_roles():
    """Check what roles are actually used in the users table"""
    db = SessionLocal()
    try:
        result = db.execute(text("""
            SELECT DISTINCT role, COUNT(*) as count
            FROM users
            GROUP BY role
            ORDER BY role;
        """))
        print("\nRoles in users table:")
        for row in result:
            print(f"  {row[0]}: {row[1]} users")
    finally:
        db.close()

def main():
    print("\n" + "="*60)
    print("  CHECKING USERROLE ENUM STATUS")
    print("="*60 + "\n")
    
    enum_values = check_current_enum_values()
    check_user_roles()
    
    print("\n" + "="*60)
    print("  ANALYSIS")
    print("="*60)
    
    has_uppercase = any(v.isupper() or v[0].isupper() for v in enum_values if v not in ['triage_specialist', 'finance_officer'])
    has_lowercase = any(v.islower() for v in enum_values)
    
    print(f"\nHas uppercase values: {has_uppercase}")
    print(f"Has lowercase values: {has_lowercase}")
    
    if has_uppercase and not has_lowercase:
        print("\n⚠️  WARNING: Database has uppercase enum values but model expects lowercase!")
        print("   This will cause login errors for triage_specialist users.")
        print("\n   The issue: Initial migration created uppercase values (RESEARCHER, ORGANIZATION)")
        print("   but later migrations added lowercase values (triage_specialist, finance_officer)")
        print("\n   SQLAlchemy model expects: researcher, organization, staff, admin, super_admin")
        print("   Database has: RESEARCHER, ORGANIZATION, STAFF, ADMIN, SUPER_ADMIN")
        print("\n   Solution: The application should work with the existing enum values.")
        print("   The triage_specialist and finance_officer values are correct (lowercase).")
    
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()
