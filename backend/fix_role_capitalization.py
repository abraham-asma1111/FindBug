"""
Fix role capitalization inconsistency in database.
All roles should be lowercase for consistency.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.orm import Session
from src.core.database import SessionLocal
from src.domain.models.user import User


def fix_role_capitalization():
    """Standardize all role values to lowercase."""
    db: Session = SessionLocal()
    
    try:
        print("=" * 80)
        print("FIXING ROLE CAPITALIZATION")
        print("=" * 80)
        
        # Find all users with uppercase roles
        uppercase_roles = db.query(User).filter(
            (User.role == 'RESEARCHER') | 
            (User.role == 'ORGANIZATION') |
            (User.role == 'ADMIN') |
            (User.role == 'TRIAGE_SPECIALIST') |
            (User.role == 'FINANCE_OFFICER')
        ).all()
        
        print(f"\nFound {len(uppercase_roles)} users with uppercase roles")
        
        if len(uppercase_roles) == 0:
            print("\n✅ All roles are already lowercase!")
            return
        
        # Count by role before fix
        print("\nBefore fix:")
        print(f"  RESEARCHER: {db.query(User).filter(User.role == 'RESEARCHER').count()}")
        print(f"  researcher: {db.query(User).filter(User.role == 'researcher').count()}")
        print(f"  ORGANIZATION: {db.query(User).filter(User.role == 'ORGANIZATION').count()}")
        print(f"  organization: {db.query(User).filter(User.role == 'organization').count()}")
        
        # Fix each user
        fixed_count = 0
        for user in uppercase_roles:
            old_role = user.role
            user.role = user.role.lower()
            print(f"  • {user.email}: {old_role} → {user.role}")
            fixed_count += 1
        
        # Commit changes
        db.commit()
        
        print(f"\n✅ Fixed {fixed_count} users")
        
        # Count by role after fix
        print("\nAfter fix:")
        print(f"  researcher: {db.query(User).filter(User.role == 'researcher').count()}")
        print(f"  organization: {db.query(User).filter(User.role == 'organization').count()}")
        print(f"  admin: {db.query(User).filter(User.role == 'admin').count()}")
        print(f"  triage_specialist: {db.query(User).filter(User.role == 'triage_specialist').count()}")
        print(f"  finance_officer: {db.query(User).filter(User.role == 'finance_officer').count()}")
        
        print("\n" + "=" * 80)
        print("✅ ROLE CAPITALIZATION FIXED")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    fix_role_capitalization()
