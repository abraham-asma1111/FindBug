#!/usr/bin/env python3
"""
Test script to create triage specialist user - handles enum issues gracefully
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from src.domain.models.user import User
from src.domain.models.staff_profiles import TriageSpecialist
from src.core.security import get_password_hash
import uuid

# Database connection
DATABASE_URL = "postgresql://bugbounty_user:changeme123@localhost:5432/bug_bounty_production"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def check_enum_values():
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
        print(f"✓ Current userrole enum values: {values}")
        return values
    finally:
        db.close()

def create_triage_specialist():
    print("\n" + "="*60)
    print("  CREATING TRIAGE SPECIALIST USER")
    print("="*60 + "\n")
    
    # Check enum values first
    enum_values = check_enum_values()
    
    if 'triage_specialist' not in enum_values:
        print("\n❌ ERROR: 'triage_specialist' not in userrole enum!")
        print("   Available values:", enum_values)
        print("\n   Run this SQL to add it:")
        print("   ALTER TYPE userrole ADD VALUE 'triage_specialist';")
        return
    
    db = SessionLocal()
    try:
        # Check if user exists using raw SQL to avoid enum issues
        result = db.execute(text("""
            SELECT id, email, role FROM users WHERE email = 'triage@example.com'
        """))
        existing_row = result.first()
        
        if existing_row:
            user_id, email, role = existing_row
            print(f"✅ Triage specialist user already exists: {email}")
            print(f"   User ID: {user_id}")
            print(f"   Role: {role}")
            
            # Check if triage specialist profile exists
            profile_result = db.execute(text("""
                SELECT id FROM triage_specialists WHERE user_id = :user_id
            """), {"user_id": user_id})
            profile_row = profile_result.first()
            
            if profile_row:
                print(f"   Triage Specialist ID: {profile_row[0]}")
            else:
                print("   ⚠️  No triage specialist profile found, creating...")
                specialist_id = uuid.uuid4()
                db.execute(text("""
                    INSERT INTO triage_specialists (id, user_id, specialization, years_experience, accuracy_rate, created_at)
                    VALUES (:id, :user_id, :specialization, :years_experience, :accuracy_rate, NOW())
                """), {
                    "id": specialist_id,
                    "user_id": user_id,
                    "specialization": '["web", "api", "mobile"]',
                    "years_experience": 3,
                    "accuracy_rate": 95.5
                })
                db.commit()
                print(f"   ✅ Created triage specialist profile: {specialist_id}")
            
            print("\n" + "="*60)
            print("  USER ALREADY EXISTS - USE EXISTING CREDENTIALS")
            print("="*60)
            print("\nLogin credentials:")
            print("  Email: triage@example.com")
            print("  Password: password123")
            print("  Portal: http://localhost:3000/triage/dashboard")
            print("="*60 + "\n")
            return
        
        # Create user using raw SQL to avoid enum issues
        user_id = uuid.uuid4()
        password_hash = get_password_hash("password123")
        
        db.execute(text("""
            INSERT INTO users (id, email, password_hash, role, is_verified, is_active, created_at)
            VALUES (:id, :email, :password_hash, 'triage_specialist', true, true, NOW())
        """), {
            "id": user_id,
            "email": "triage@example.com",
            "password_hash": password_hash
        })
        db.commit()
        
        print(f"✅ Created user: triage@example.com")
        print(f"   User ID: {user_id}")
        print(f"   Role: triage_specialist")
        
        # Create triage specialist profile
        specialist_id = uuid.uuid4()
        db.execute(text("""
            INSERT INTO triage_specialists (id, user_id, specialization, years_experience, accuracy_rate, created_at)
            VALUES (:id, :user_id, :specialization, :years_experience, :accuracy_rate, NOW())
        """), {
            "id": specialist_id,
            "user_id": user_id,
            "specialization": '["web", "api", "mobile"]',
            "years_experience": 3,
            "accuracy_rate": 95.5
        })
        db.commit()
        
        print(f"✅ Created triage specialist profile: {specialist_id}")
        print(f"   Specialization: [\"web\", \"api\", \"mobile\"]")
        print(f"   Years Experience: 3")
        print(f"   Accuracy Rate: 95.5%")
        
        print("\n" + "="*60)
        print("  SUCCESS!")
        print("="*60)
        print("\nLogin credentials:")
        print("  Email: triage@example.com")
        print("  Password: password123")
        print("\nAccess the Triage Portal:")
        print("  1. Start the frontend: cd frontend && npm run dev")
        print("  2. Start the backend: cd backend && uvicorn src.main:app --reload")
        print("  3. Login at: http://localhost:3000")
        print("  4. You'll be redirected to: http://localhost:3000/triage/dashboard")
        print("\nAvailable Triage Portal Pages:")
        print("  • Dashboard:    /triage/dashboard")
        print("  • Queue:        /triage/queue")
        print("  • Reports:      /triage/reports")
        print("  • Duplicates:   /triage/duplicates")
        print("  • Templates:    /triage/templates ✨ NEW")
        print("  • Analytics:    /triage/analytics")
        print("  • Researchers:  /triage/researchers ✨ NEW")
        print("  • Programs:     /triage/programs ✨ NEW")
        print("  • Messages:     /triage/messages")
        print("="*60 + "\n")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    create_triage_specialist()
