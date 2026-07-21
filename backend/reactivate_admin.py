#!/usr/bin/env python3
"""
Script to reactivate a deactivated admin user
"""
import asyncio
from sqlalchemy import select, update
from src.core.database import get_db
from src.domain.models.user import User


async def reactivate_admin():
    """Reactivate admin user"""
    db_gen = get_db()
    db = await anext(db_gen)
    try:
        # Get all admin users
        result = await db.execute(
            select(User).where(User.role == 'admin')
        )
        admins = result.scalars().all()
        
        if not admins:
            print("❌ No admin users found in database")
            return
        
        print("\n📋 Admin Users:")
        print("-" * 80)
        for idx, admin in enumerate(admins, 1):
            status = "✅ ACTIVE" if admin.is_active else "❌ INACTIVE"
            print(f"{idx}. {admin.email}")
            print(f"   Name: {admin.full_name or 'N/A'}")
            print(f"   ID: {admin.id}")
            print(f"   Status: {status}")
            print(f"   Created: {admin.created_at}")
            print("-" * 80)
        
        # Ask which admin to reactivate
        print("\nEnter the number of the admin to reactivate (or 'all' for all inactive admins):")
        choice = input("Choice: ").strip().lower()
        
        if choice == 'all':
            # Reactivate all inactive admins
            inactive_admins = [a for a in admins if not a.is_active]
            if not inactive_admins:
                print("\n✅ All admin users are already active!")
                return
            
            for admin in inactive_admins:
                admin.is_active = True
            await db.commit()
            for admin in inactive_admins:
                print(f"✅ Reactivated: {admin.email}")
            
            print(f"\n✅ Successfully reactivated {len(inactive_admins)} admin user(s)")
        else:
            try:
                idx = int(choice) - 1
                if idx < 0 or idx >= len(admins):
                    print("❌ Invalid choice")
                    return
                
                admin = admins[idx]
                if admin.is_active:
                    print(f"\n✅ {admin.email} is already active!")
                else:
                    admin.is_active = True
                    await db.commit()
                    print(f"\n✅ Successfully reactivated: {admin.email}")
                    print(f"   You can now log in with this account")
            except ValueError:
                print("❌ Invalid input. Please enter a number or 'all'")
                    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        await db.rollback()
    finally:
        await db.close()


if __name__ == "__main__":
    print("🔧 Admin User Reactivation Tool")
    print("=" * 80)
    asyncio.run(reactivate_admin())
