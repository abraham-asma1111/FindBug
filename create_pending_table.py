#!/usr/bin/env python3
"""
Create pending_registrations table manually
"""
import os
from dotenv import load_dotenv
load_dotenv('backend/.env')

import sys
sys.path.append('backend/src')

from sqlalchemy import create_engine, text

def create_pending_table():
    """Create pending_registrations table manually"""
    print("🔧 Creating pending_registrations table...")
    
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/bugbounty')
    engine = create_engine(database_url)
    
    try:
        with engine.connect() as conn:
            # Start transaction
            trans = conn.begin()
            
            try:
                # Check if table exists
                result = conn.execute(text("""
                    SELECT tablename FROM pg_tables 
                    WHERE tablename = 'pending_registrations'
                """))
                
                if result.fetchone():
                    print("✅ Table already exists!")
                    return True
                
                # Create the table
                conn.execute(text("""
                    CREATE TABLE pending_registrations (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        email VARCHAR(255) NOT NULL,
                        password_hash VARCHAR(255) NOT NULL,
                        role VARCHAR(50) NOT NULL,
                        first_name VARCHAR(100) NOT NULL,
                        last_name VARCHAR(100) NOT NULL,
                        company_name VARCHAR(200),
                        phone_number VARCHAR(20),
                        country VARCHAR(100),
                        verification_token VARCHAR(255) NOT NULL,
                        created_at TIMESTAMP DEFAULT NOW(),
                        expires_at TIMESTAMP NOT NULL
                    )
                """))
                
                # Create indexes separately
                conn.execute(text("""
                    CREATE UNIQUE INDEX IF NOT EXISTS idx_pending_email ON pending_registrations(email)
                """))
                
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_pending_token ON pending_registrations(verification_token)
                """))
                
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_pending_expires ON pending_registrations(expires_at)
                """))
                
                # Commit transaction
                trans.commit()
                print("✅ Table created successfully!")
                
                return True
                
            except Exception as e:
                trans.rollback()
                print(f"❌ Error creating table: {e}")
                return False
                
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False

if __name__ == "__main__":
    create_pending_table()