"""
Create test researcher users for PTaaS testing
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.orm import Session
from src.core.database import SessionLocal, engine
from src.domain.models.user import User
from src.domain.models.researcher import Researcher
from src.core.security import get_password_hash
from datetime import datetime
from uuid import uuid4

def create_test_researchers():
    """Create test researcher accounts"""
    db: Session = SessionLocal()
    
    try:
        researchers_data = [
            {
                "email": "researcher1@test.com",
                "username": "researcher1",
                "full_name": "John Doe",
                "reputation_score": 8500,
                "specialties": ["Web Security", "API Testing"],
            },
            {
                "email": "researcher2@test.com",
                "username": "researcher2",
                "full_name": "Jane Smith",
                "reputation_score": 9200,
                "specialties": ["Mobile Security", "Cloud Security"],
            },
            {
                "email": "researcher3@test.com",
                "username": "researcher3",
                "full_name": "Bob Johnson",
                "reputation_score": 7800,
                "specialties": ["Network Security", "IoT Security"],
            },
            {
                "email": "researcher4@test.com",
                "username": "researcher4",
                "full_name": "Alice Williams",
                "reputation_score": 8900,
                "specialties": ["Web Security", "Mobile Security"],
            },
        ]
        
        created_researchers = []
        
        for data in researchers_data:
            # Check if user already exists
            existing_user = db.query(User).filter(User.email == data["email"]).first()
            if existing_user:
                print(f"✓ User {data['email']} already exists")
                continue
            
            # Create user
            user = User(
                id=uuid4(),
                email=data["email"],
                username=data["username"],
                full_name=data["full_name"],
                hashed_password=get_password_hash("password123"),
                role="researcher",
                is_active=True,
                is_verified=True,
                created_at=datetime.utcnow(),
            )
            db.add(user)
            db.flush()
            
            # Create researcher profile
            researcher = Researcher(
                id=uuid4(),
                user_id=user.id,
                reputation_score=data["reputation_score"],
                rank="Elite" if data["reputation_score"] > 9000 else "Advanced" if data["reputation_score"] > 8000 else "Intermediate",
                total_reports_submitted=50,
                accepted_reports=40,
                total_earnings=data["reputation_score"] * 10,
                specialties=data["specialties"],
                bio=f"Experienced security researcher specializing in {', '.join(data['specialties'])}",
                created_at=datetime.utcnow(),
            )
            db.add(researcher)
            
            created_researchers.append({
                "email": data["email"],
                "user_id": str(user.id),
                "researcher_id": str(researcher.id),
            })
            
            print(f"✓ Created researcher: {data['full_name']} ({data['email']})")
        
        db.commit()
        
        print(f"\n✅ Successfully created {len(created_researchers)} researchers")
        print("\nLogin credentials:")
        print("Email: researcher1@test.com (or researcher2, researcher3, researcher4)")
        print("Password: password123")
        
        print("\nResearcher IDs for API testing:")
        for r in created_researchers:
            print(f"  {r['email']}: {r['user_id']}")
        
        return created_researchers
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating researchers: {e}")
        import traceback
        traceback.print_exc()
        return []
    finally:
        db.close()


if __name__ == "__main__":
    print("Creating test researchers...\n")
    create_test_researchers()
