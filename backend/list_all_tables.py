#!/usr/bin/env python3
"""
List all tables in the database
"""
from sqlalchemy import create_engine, text, inspect
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/bugbounty")

def list_tables():
    """List all tables in database"""
    engine = create_engine(DATABASE_URL)
    inspector = inspect(engine)
    
    print("=" * 80)
    print("ALL TABLES IN DATABASE")
    print("=" * 80)
    
    tables = inspector.get_table_names()
    
    if tables:
        print(f"\nFound {len(tables)} tables:")
        for i, table in enumerate(sorted(tables), 1):
            print(f"{i:3}. {table}")
            
            # Get row count for each table
            with engine.connect() as conn:
                try:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.scalar()
                    print(f"     → {count} rows")
                except Exception as e:
                    print(f"     → Error counting: {e}")
    else:
        print("\nNo tables found in database!")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    list_tables()
