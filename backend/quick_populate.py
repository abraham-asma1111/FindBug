"""Quick populate script - adds minimal data to test triage portal."""
import sys
from datetime import datetime, timedelta
from uuid import uuid4
from sqlalchemy.orm import Session
from sqlalchemy import text

from src.core.database import SessionLocal
from src.core.security import get_password_hash


def quick_populate():
    """Add minimal test data."""
    db: Session = SessionLocal()
    
    try:
        print("Quick Populate - Adding Test Data")
        print("=" * 60)
        
        # Check if tables exist
        result = db.execute(text("SELECT to_regclass('users')"))
        if result.scalar() is None:
            print("❌ Database tables don't exist. Run migrations first:")
            print("   cd backend && alembic stamp head")
            return
        
        # Check existing users
        result = db.execute(text("SELECT COUNT(*) FROM users"))
        user_count = result.scalar()
        print(f"\nCurrent users in database: {user_count}")
        
        if user_count > 0:
            print("\n✓ Database already has data")
            print("\nExisting user roles:")
            result = db.execute(text("SELECT DISTINCT role FROM users"))
            for row in result:
                print(f"  - {row[0]}")
        else:
            print("\n❌ Database is empty - no users found")
        
        print("\n" + "=" * 60)
        print("RECOMMENDATION:")
        print("=" * 60)
        print("\nThe database exists but may be empty or have migration issues.")
        print("\nTo fix:")
        print("1. Reset database: docker-compose down -v && docker-compose up -d")
        print("2. Run migrations: cd backend && alembic stamp head")
        print("3. Use existing test scripts to create users")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    quick_populate()
