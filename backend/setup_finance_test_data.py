"""Setup Finance Portal Test Data"""

import asyncio
from sqlalchemy.orm import Session
from src.core.database import get_db
from src.domain.models.user import User, UserRole
from src.core.security import get_password_hash

async def create_finance_user():
    """Create finance officer user for testing"""
    db = next(get_db())
    
    try:
        # Check if finance user exists
        existing = db.query(User).filter(User.email == "finance@securecrowd.com").first()
        if existing:
            print("✅ Finance user already exists")
            return
        
        # Create finance user
        finance_user = User(
            email="finance@securecrowd.com",
            password_hash=get_password_hash("Finance123!"),
            role=UserRole.FINANCE_OFFICER,
            full_name="Finance Officer",
            is_active=True,
            is_verified=True
        )
        
        db.add(finance_user)
        db.commit()
        
        print("✅ Finance user created successfully")
        print(f"   Email: finance@securecrowd.com")
        print(f"   Password: Finance123!")
        print(f"   Role: {UserRole.FINANCE_OFFICER}")
        
    except Exception as e:
        print(f"❌ Error creating finance user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(create_finance_user())
