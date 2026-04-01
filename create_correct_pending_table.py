#!/usr/bin/env python3
"""
Create pending_registrations table with correct structure matching the model
"""
import os
from dotenv import load_dotenv
load_dotenv('backend/.env')

import sys
sys.path.append('backend/src')

from sqlalchemy import create_engine, text

def create_correct_pending_table():
    """Create pending_registrations table with all columns matching the model"""
    print("🔧 Creating correct pending_registrations table...")
    
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/bugbounty')
    engine = create_engine(database_url)
    
    try:
        with engine.connect() as conn:
            # Start transaction
            trans = conn.begin()
            
            try:
                # Drop table if exists
                conn.execute(text("DROP TABLE IF EXISTS pending_registrations CASCADE"))
                
                # Create the table with all columns from the model
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
                        verification_otp VARCHAR(10),
                        otp_expires_at TIMESTAMP,
                        created_at TIMESTAMP DEFAULT NOW() NOT NULL,
                        expires_at TIMESTAMP NOT NULL,
                        verified_at TIMESTAMP,
                        is_verified BOOLEAN DEFAULT FALSE NOT NULL,
                        ip_address VARCHAR(45),
                        user_agent TEXT
                    )
                """))
                
                # Create indexes
                conn.execute(text("""
                    CREATE UNIQUE INDEX IF NOT EXISTS idx_pending_email ON pending_registrations(email)
                """))
                
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_pending_token ON pending_registrations(verification_token)
                """))
                
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_pending_expires ON pending_registrations(expires_at)
                """))
                
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_pending_created ON pending_registrations(created_at)
                """))
                
                # Commit transaction
                trans.commit()
                print("✅ Table created successfully with all columns!")
                
                return True
                
            except Exception as e:
                trans.rollback()
                print(f"❌ Error creating table: {e}")
                return False
                
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False

if __name__ == "__main__":
    create_correct_pending_table()