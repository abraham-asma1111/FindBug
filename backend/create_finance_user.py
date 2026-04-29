#!/usr/bin/env python3
"""
Create Finance Officer User for Testing
"""
import sys
from src.core.database import SessionLocal
from src.domain.models.user import User
from src.domain.models.staff_profiles import FinancialOfficer
from src.core.security import get_password_hash

def create_finance_officer():
    """Create a finance officer user for testing"""
    
    db = SessionLocal()
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == "finance@findbug.com").first()
        
        if existing_user:
            print("✅ Finance officer already exists!")
            print(f"   Email: finance@findbug.com")
            print(f"   Password: Finance123!")
            print(f"   Role: {existing_user.role}")
            return
        
        # Create finance officer user
        finance_user = User(
            email="finance@findbug.com",
            password_hash=get_password_hash("Finance123!"),
            role="finance_officer",
            is_verified=True,
            mfa_enabled=False,
            is_active=True
        )
        
        db.add(finance_user)
        db.flush()
        
        # Create financial officer profile
        finance_profile = FinancialOfficer(
            user_id=finance_user.id,
            department="finance",
            approval_limit=100000.00  # 100,000 ETB approval limit
        )
        
        db.add(finance_profile)
        db.commit()
        
        print("✅ Finance officer created successfully!")
        print(f"   Email: finance@findbug.com")
        print(f"   Password: Finance123!")
        print(f"   Role: finance_officer")
        print(f"   User ID: {finance_user.id}")
        print(f"   Approval Limit: 100,000 ETB")
        print(f"\n🔐 Login at: http://localhost:3000")
        print(f"\n📋 Test the Finance Portal:")
        print(f"   1. Login with the credentials above")
        print(f"   2. You'll be redirected to /finance/dashboard")
        print(f"   3. Check the sidebar structure matches specification")
        print(f"   4. Navigate through all pages")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating finance officer: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    print("Creating Finance Officer User...")
    create_finance_officer()
