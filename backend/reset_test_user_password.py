"""
Reset password for test user to enable testing.
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.security import get_password_hash
from src.domain.models.user import User

load_dotenv()

# Database connection
db_url = os.getenv('DATABASE_URL')
engine = create_engine(db_url)
SessionLocal = sessionmaker(bind=engine)

def reset_password():
    """Reset password for test researcher user."""
    db = SessionLocal()
    
    try:
        # Get user
        user = db.query(User).filter(User.email == "foyihob867@justnapa.com").first()
        
        if not user:
            print("❌ User not found")
            return False
        
        # Reset password
        new_password = "Password123!"
        user.password_hash = get_password_hash(new_password)
        
        db.commit()
        
        print(f"✅ Password reset successful for {user.email}")
        print(f"   New password: {new_password}")
        print(f"   Role: {user.role}")
        print(f"   Verified: {user.is_verified}")
        print(f"   Active: {user.is_active}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("RESET TEST USER PASSWORD")
    print("=" * 60)
    reset_password()
