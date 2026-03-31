#!/usr/bin/env python3
"""
Create pending_registrations table directly
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from src.core.config import settings

def create_pending_registrations_table():
    """Create pending_registrations table"""
    
    engine = create_engine(settings.DATABASE_URL)
    
    sql = """
    DO $$ 
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'registrationtype') THEN
            CREATE TYPE registrationtype AS ENUM ('researcher', 'organization');
        END IF;
    END $$;
    
    CREATE TABLE IF NOT EXISTS pending_registrations (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        email VARCHAR(255) NOT NULL UNIQUE,
        password_hash VARCHAR(255) NOT NULL,
        registration_type registrationtype NOT NULL,
        first_name VARCHAR(100) NOT NULL,
        last_name VARCHAR(100) NOT NULL,
        company_name VARCHAR(200),
        phone_number VARCHAR(20),
        country VARCHAR(100),
        verification_token VARCHAR(255) NOT NULL,
        verification_otp VARCHAR(10),
        otp_expires_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT NOW(),
        expires_at TIMESTAMP NOT NULL,
        verified_at TIMESTAMP,
        is_verified BOOLEAN DEFAULT FALSE,
        ip_address VARCHAR(45),
        user_agent TEXT
    );

    CREATE INDEX IF NOT EXISTS ix_pending_registrations_email ON pending_registrations(email);
    CREATE INDEX IF NOT EXISTS ix_pending_registrations_verification_token ON pending_registrations(verification_token);
    CREATE INDEX IF NOT EXISTS ix_pending_registrations_expires_at ON pending_registrations(expires_at);
    CREATE INDEX IF NOT EXISTS ix_pending_registrations_created_at ON pending_registrations(created_at);
    """
    
    try:
        with engine.connect() as conn:
            conn.execute(text(sql))
            conn.commit()
        print("✅ Created pending_registrations table successfully!")
        return True
    except Exception as e:
        print(f"❌ Error creating table: {e}")
        return False

if __name__ == "__main__":
    create_pending_registrations_table()