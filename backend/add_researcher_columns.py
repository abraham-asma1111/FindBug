#!/usr/bin/env python3
"""
Add missing columns to researchers table
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import create_engine, text

# Use the correct database URL from docker-compose
DATABASE_URL = "postgresql://bugbounty_user:changeme123@localhost:5432/bug_bounty_production"

def add_columns():
    print("\n" + "="*60)
    print("  ADDING MISSING COLUMNS TO RESEARCHERS TABLE")
    print("="*60 + "\n")
    
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # Check if columns exist
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='researchers' AND column_name IN ('total_reports', 'verified_reports', 'is_active')
        """))
        existing = [row[0] for row in result]
        print(f"Existing columns: {existing}\n")
        
        # Add missing columns
        if 'total_reports' not in existing:
            conn.execute(text('ALTER TABLE researchers ADD COLUMN total_reports INTEGER DEFAULT 0'))
            conn.commit()
            print('✅ Added total_reports column')
        else:
            print('⏭️  total_reports column already exists')
        
        if 'verified_reports' not in existing:
            conn.execute(text('ALTER TABLE researchers ADD COLUMN verified_reports INTEGER DEFAULT 0'))
            conn.commit()
            print('✅ Added verified_reports column')
        else:
            print('⏭️  verified_reports column already exists')
        
        if 'is_active' not in existing:
            conn.execute(text('ALTER TABLE researchers ADD COLUMN is_active BOOLEAN DEFAULT true'))
            conn.commit()
            print('✅ Added is_active column')
        else:
            print('⏭️  is_active column already exists')
        
        print("\n" + "="*60)
        print("  MIGRATION COMPLETE!")
        print("="*60 + "\n")

if __name__ == "__main__":
    try:
        add_columns()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
