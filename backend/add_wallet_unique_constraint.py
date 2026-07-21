"""
Add unique constraint to wallets table directly.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import text
from src.core.database import SessionLocal

def add_constraint():
    """Add unique constraint to wallets table."""
    db = SessionLocal()
    
    try:
        print("\n" + "="*80)
        print("ADDING UNIQUE CONSTRAINT TO WALLETS TABLE")
        print("="*80)
        
        # Check if constraint already exists
        print("\n[1] Checking if constraint already exists...")
        result = db.execute(text("""
            SELECT constraint_name 
            FROM information_schema.table_constraints 
            WHERE table_name = 'wallets' 
            AND constraint_name = 'uq_wallets_owner_id_owner_type'
        """))
        
        existing = result.fetchone()
        if existing:
            print("   ✅ Constraint already exists!")
            return
        
        print("   Constraint does not exist, adding it...")
        
        # Add the unique constraint
        print("\n[2] Adding unique constraint...")
        db.execute(text("""
            ALTER TABLE wallets 
            ADD CONSTRAINT uq_wallets_owner_id_owner_type 
            UNIQUE (owner_id, owner_type)
        """))
        
        db.commit()
        
        print("   ✅ Constraint added successfully!")
        
        # Verify
        print("\n[3] Verifying constraint...")
        result = db.execute(text("""
            SELECT constraint_name, constraint_type
            FROM information_schema.table_constraints 
            WHERE table_name = 'wallets' 
            AND constraint_name = 'uq_wallets_owner_id_owner_type'
        """))
        
        constraint = result.fetchone()
        if constraint:
            print(f"   ✅ Verified: {constraint[0]} ({constraint[1]})")
        else:
            print("   ❌ Constraint not found after adding!")
        
        print("\n" + "="*80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_constraint()
