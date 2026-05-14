"""
Check ALL user roles in database
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.orm import Session
from sqlalchemy import func
from src.core.database import SessionLocal
from src.domain.models.user import User


def check_all_roles():
    """Check all user roles."""
    db: Session = SessionLocal()
    
    try:
        print("=" * 80)
        print("ALL USER ROLES IN DATABASE")
        print("=" * 80)
        
        # Get count by role
        role_counts = db.query(
            User.role,
            func.count(User.id).label('count')
        ).group_by(User.role).all()
        
        total = db.query(User).count()
        
        print(f"\nTotal Users: {total}\n")
        print("Breakdown by Role:")
        print("-" * 80)
        
        for role, count in role_counts:
            print(f"  {role}: {count}")
        
        print("-" * 80)
        
        # Show sample users for each role
        print("\nSample Users by Role:")
        print("=" * 80)
        
        for role, count in role_counts:
            print(f"\n{role.upper()} ({count} users):")
            users = db.query(User).filter(User.role == role).limit(5).all()
            for user in users:
                print(f"  • {user.email}")
        
        print("\n" + "=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    check_all_roles()
