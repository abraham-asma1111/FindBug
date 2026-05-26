#!/usr/bin/env python3
"""Check the actual schema of vulnerability_reports table."""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from src.core.config import settings

# Create database connection
engine = create_engine(settings.DATABASE_URL)
Session = sessionmaker(bind=engine)
db = Session()

print("=" * 80)
print("VULNERABILITY_REPORTS TABLE SCHEMA")
print("=" * 80)

# Get table columns using inspector
inspector = inspect(engine)
columns = inspector.get_columns('vulnerability_reports')

print("\nColumns in vulnerability_reports table:")
for col in columns:
    nullable = "NULL" if col['nullable'] else "NOT NULL"
    print(f"  - {col['name']:<30} {str(col['type']):<20} {nullable}")

print("\n" + "=" * 80)

# Now let's get a sample report to see what data exists
print("\nSAMPLE REPORT DATA:")
sample_query = text("""
    SELECT *
    FROM vulnerability_reports
    WHERE deleted_at IS NULL
    LIMIT 1
""")
result = db.execute(sample_query).fetchone()

if result:
    print("\nSample report columns and values:")
    for key in result._mapping.keys():
        value = result._mapping[key]
        print(f"  {key}: {value}")
else:
    print("  No reports found")

print("\n" + "=" * 80)

db.close()
