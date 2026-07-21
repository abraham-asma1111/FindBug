"""Reset triage specialist password."""
from sqlalchemy.orm import Session
from sqlalchemy import text

from src.core.database import SessionLocal
from src.core.security import get_password_hash

def reset_password():
    """Reset triage specialist password."""
    db: Session = SessionLocal()
    
    try:
        print("Resetting triage specialist password...")
        
        # New password
        new_password = "Password123!"
        password_hash = get_password_hash(new_password)
        
        # Update password
        result = db.execute(
            text("UPDATE users SET password_hash = :hash WHERE email = 'triage@example.com'"),
            {"hash": password_hash}
        )
        db.commit()
        
        print(f"✓ Password reset successful")
        print(f"\nLogin credentials:")
        print(f"  Email: triage@example.com")
        print(f"  Password: {new_password}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    reset_password()
