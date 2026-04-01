#!/usr/bin/env python3
"""
Fix pending_registrations table by adding missing columns
"""
import os
from dotenv import load_dotenv
load_dotenv('backend/.env')

import sys
sys.path.append('backend/src')

from sqlalchemy import create_engine, text

def fix_pending_table():
    """Add missing columns to pending_registrations table"""
    print("🔧 Adding missing columns to pending_registrations table...")
    
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/bugbounty')
    engine = create_engine(database_url)
    
    try:
        with engine.connect() as conn:
            # Start transaction
            trans = conn.begin()
            
            try:
                # Add missing columns one by one
                missing_columns = [
                    "ALTER TABLE pending_registrations ADD COLUMN IF NOT EXISTS verification_otp VARCHAR(10)",
                    "ALTER TABLE pending_registrations ADD COLUMN IF NOT EXISTS otp_expires_at TIMESTAMP",
                    "ALTER TABLE pending_registrations ADD COLUMN IF NOT EXISTS verified_at TIMESTAMP",
                    "ALTER TABLE pending_registrations ADD COLUMN IF NOT EXISTS is_verified BOOLEAN DEFAULT FALSE",
                    "ALTER TABLE pending_registrations ADD COLUMN IF NOT EXISTS ip_address VARCHAR(45)",
                    "ALTER TABLE pending_registrations ADD COLUMN IF NOT EXISTS user_agent TEXT"
                ]
                
                for sql in missing_columns:
                    print(f"Executing: {sql}")
                    conn.execute(text(sql))
                
                # Commit transaction
                trans.commit()
                print("✅ All missing columns added successfully!")
                
                return True
                
            except Exception as e:
                trans.rollback()
                print(f"❌ Error adding columns: {e}")
                return False
                
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False

if __name__ == "__main__":
    fix_pending_table()