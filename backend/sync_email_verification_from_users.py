#!/usr/bin/env python3
"""
Sync email verification status from users table to KYC records.

This script updates KYC records to reflect email verification status
from the users table (email_verified_at field).

Usage:
    cd backend
    python sync_email_verification_from_users.py
"""

import sys
import os
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database connection
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://bugbounty_user:changeme123@localhost:5432/bug_bounty_production"
)

def sync_email_verification():
    """Sync email verification status from users to KYC records."""
    
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        logger.info("Starting email verification sync...")
        
        # SQL to update KYC records based on users.email_verified_at
        sync_query = text("""
            UPDATE kyc_verifications
            SET 
                email_verified = TRUE,
                email_verified_at = users.email_verified_at,
                email_address = users.email
            FROM users
            WHERE 
                kyc_verifications.user_id = users.id
                AND users.email_verified_at IS NOT NULL
                AND kyc_verifications.email_verified = FALSE;
        """)
        
        result = session.execute(sync_query)
        session.commit()
        
        rows_updated = result.rowcount
        logger.info(f"✅ Successfully updated {rows_updated} KYC records")
        
        # Show updated records
        check_query = text("""
            SELECT 
                u.email,
                u.email_verified_at as user_verified_at,
                k.email_verified as kyc_email_verified,
                k.email_verified_at as kyc_verified_at
            FROM users u
            LEFT JOIN kyc_verifications k ON k.user_id = u.id
            WHERE u.email_verified_at IS NOT NULL
            ORDER BY u.email;
        """)
        
        results = session.execute(check_query).fetchall()
        
        if results:
            logger.info("\n📋 Current status:")
            logger.info("-" * 80)
            for row in results:
                logger.info(f"Email: {row.email}")
                logger.info(f"  User verified at: {row.user_verified_at}")
                logger.info(f"  KYC email_verified: {row.kyc_email_verified}")
                logger.info(f"  KYC verified at: {row.kyc_verified_at}")
                logger.info("-" * 80)
        
        return rows_updated
        
    except Exception as e:
        logger.error(f"❌ Error syncing email verification: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    try:
        rows_updated = sync_email_verification()
        
        if rows_updated > 0:
            logger.info(f"\n✅ Sync complete! Updated {rows_updated} KYC records.")
            logger.info("Users who verified email during registration now have email_verified=TRUE in KYC.")
        else:
            logger.info("\n✅ Sync complete! No records needed updating.")
            logger.info("All KYC records are already in sync with user email verification status.")
        
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"\n❌ Sync failed: {e}")
        sys.exit(1)
