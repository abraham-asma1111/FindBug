#!/usr/bin/env python3
"""
Drop manually created pending_registrations table so we can run proper migration
"""
import os
from dotenv import load_dotenv
load_dotenv('backend/.env')

import sys
sys.path.append('backend/src')

from sqlalchemy import create_engine, text

def drop_pending_table():
    """Drop manually created pending_registrations table"""
    print("🗑️ Dropping manually created pending_registrations table...")
    
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/bugbounty')
    engine = create_engine(database_url)
    
    try:
        with engine.connect() as conn:
            # Start transaction
            trans = conn.begin()
            
            try:
                # Drop the table if it exists
                conn.execute(text("DROP TABLE IF EXISTS pending_registrations CASCADE"))
                
                # Commit transaction
                trans.commit()
                print("✅ Table dropped successfully!")
                
                return True
                
            except Exception as e:
                trans.rollback()
                print(f"❌ Error dropping table: {e}")
                return False
                
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False

if __name__ == "__main__":
    drop_pending_table()