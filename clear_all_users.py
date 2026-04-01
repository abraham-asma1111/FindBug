#!/usr/bin/env python3
"""
Clear All Users from Database
"""
import os
from dotenv import load_dotenv
load_dotenv('backend/.env')

import sys
sys.path.append('backend/src')

from sqlalchemy import create_engine, text

def clear_all_users():
    """Clear all users and related data from database"""
    print("🗑️  Clearing all users from database...")
    
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/bugbounty')
    engine = create_engine(database_url)
    
    try:
        with engine.connect() as conn:
            # Start transaction
            trans = conn.begin()
            
            try:
                # Delete in correct order to avoid foreign key constraints
                print("   Deleting researchers...")
                conn.execute(text("DELETE FROM researchers"))
                
                print("   Deleting organizations...")
                conn.execute(text("DELETE FROM organizations"))
                
                print("   Deleting users...")
                conn.execute(text("DELETE FROM users"))
                
                # Commit transaction
                trans.commit()
                print("✅ All users cleared successfully!")
                
                # Show counts
                result = conn.execute(text("SELECT COUNT(*) FROM users"))
                user_count = result.scalar()
                
                result = conn.execute(text("SELECT COUNT(*) FROM researchers"))
                researcher_count = result.scalar()
                
                result = conn.execute(text("SELECT COUNT(*) FROM organizations"))
                org_count = result.scalar()
                
                print(f"   Users: {user_count}")
                print(f"   Researchers: {researcher_count}")
                print(f"   Organizations: {org_count}")
                
            except Exception as e:
                trans.rollback()
                print(f"❌ Error clearing users: {e}")
                return False
                
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    clear_all_users()