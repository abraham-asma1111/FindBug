"""Create a fresh test researcher for testing."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.orm import Session
from src.core.database import SessionLocal
from src.domain.models.user import User
from src.domain.models.researcher import Researcher
from src.core.security import get_password_hash
import uuid

def create_fresh_researcher():
    """Create a fresh researcher account for testing."""
    db: Session = SessionLocal()
    
    try:
        email = "test.researcher.fresh@example.com"
        password = "TestPass123!"
        
        # Check if user exists
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            db.delete(existing)
            db.commit()
            print(f"Deleted existing user: {email}")
        
        # Create user
        user = User(
            id=uuid.uuid4(),
            email=email,
            password_hash=get_password_hash(password),
            role="RESEARCHER",
            is_active=True,
            is_verified=True
        )
        db.add(user)
        db.flush()
        
        # Create researcher profile
        researcher = Researcher(
            id=uuid.uuid4(),
            user_id=user.id,
            username="TestResearcher",
            reputation_score=100
        )
        db.add(researcher)
        
        db.commit()
        
        print("✅ Fresh researcher created successfully!")
        print(f"Email: {email}")
        print(f"Password: {password}")
        print(f"User ID: {user.id}")
        print(f"Researcher ID: {researcher.id}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_fresh_researcher()
