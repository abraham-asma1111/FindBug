#!/usr/bin/env python3
"""
Check table schemas
"""
from sqlalchemy import create_engine, text, inspect
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/bugbounty")

def check_schemas():
    """Check schemas of key tables"""
    engine = create_engine(DATABASE_URL)
    inspector = inspect(engine)
    
    tables_to_check = [
        'vulnerability_reports',
        'bounty_programs',
        'program_participations',
        'researchers',
        'organizations'
    ]
    
    for table_name in tables_to_check:
        print("=" * 80)
        print(f"TABLE: {table_name}")
        print("=" * 80)
        
        columns = inspector.get_columns(table_name)
        print(f"\nColumns ({len(columns)}):")
        for col in columns:
            nullable = "NULL" if col['nullable'] else "NOT NULL"
            default = f" DEFAULT {col['default']}" if col['default'] else ""
            print(f"  - {col['name']:<30} {str(col['type']):<20} {nullable}{default}")
        
        print()

if __name__ == "__main__":
    check_schemas()
