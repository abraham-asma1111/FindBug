"""Create platform user for platform wallet."""
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from uuid import UUID

load_dotenv()

# Setup database
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    from src.domain.models.user import User, UserRole
    
    # Platform user ID
    platform_user_id = UUID('00000000-0000-0000-0000-000000000000')
    
    # Check if platform user exists
    platform_user = db.query(User).filter(User.id == platform_user_id).first()
    
    if platform_user:
        print(f"✅ Platform user already exists:")
        print(f"   ID: {platform_user.id}")
        print(f"   Email: {platform_user.email}")
        print(f"   Role: {platform_user.role}")
    else:
        # Create platform user
        platform_user = User(
            id=platform_user_id,
            email="platform@findbug.com",
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True
        )
        # Set a dummy password hash (platform user won't log in)
        platform_user.password_hash = "PLATFORM_USER_NO_LOGIN"
        platform_user.email_verified_at = db.execute(text("SELECT NOW()")).scalar()
        
        db.add(platform_user)
        db.commit()
        db.refresh(platform_user)
        
        print(f"✅ Platform user created:")
        print(f"   ID: {platform_user.id}")
        print(f"   Email: {platform_user.email}")
        print(f"   Role: {platform_user.role}")
        print(f"\n💡 This user is used for the platform wallet to accumulate commissions")
    
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
