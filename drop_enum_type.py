#!/usr/bin/env python3
"""
Drop the registrationtype enum so we can run proper migration
"""
import os
from dotenv import load_dotenv
load_dotenv('backend/.env')

import sys
sys.path.append('backend/src')

from sqlalchemy import create_engine, text

def drop_enum_type():
    """Drop registrationtype enum"""
    print("🗑️ Dropping registrationtype enum...")
    
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/bugbounty')
    engine = create_engine(database_url)
    
    try:
        with engine.connect() as conn:
            # Start transaction
            trans = conn.begin()
            
            try:
                # Drop the enum type if it exists
                conn.execute(text("DROP TYPE IF EXISTS registrationtype CASCADE"))
                
                # Commit transaction
                trans.commit()
                print("✅ Enum type dropped successfully!")
                
                return True
                
            except Exception as e:
                trans.rollback()
                print(f"❌ Error dropping enum: {e}")
                return False
                
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False

if __name__ == "__main__":
    drop_enum_type()