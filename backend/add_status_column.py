"""
Add status column to payment_methods table for tracking rejected methods
"""
from src.core.database import SessionLocal, engine
from sqlalchemy import text

db = SessionLocal()

try:
    # Add status column with default 'pending'
    db.execute(text("""
        ALTER TABLE payment_methods 
        ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'pending'
    """))
    
    # Update existing records based on is_verified
    db.execute(text("""
        UPDATE payment_methods 
        SET status = CASE 
            WHEN is_verified = true THEN 'approved'
            ELSE 'pending'
        END
    """))
    
    # Add rejection_reason column for storing why it was rejected
    db.execute(text("""
        ALTER TABLE payment_methods 
        ADD COLUMN IF NOT EXISTS rejection_reason TEXT
    """))
    
    # Add rejected_at timestamp
    db.execute(text("""
        ALTER TABLE payment_methods 
        ADD COLUMN IF NOT EXISTS rejected_at TIMESTAMP
    """))
    
    db.commit()
    print("✓ Successfully added status, rejection_reason, and rejected_at columns")
    print("✓ Updated existing records")
    
except Exception as e:
    db.rollback()
    print(f"✗ Error: {e}")
finally:
    db.close()
