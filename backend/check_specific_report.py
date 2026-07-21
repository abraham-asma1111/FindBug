#!/usr/bin/env python3
"""Check specific report and database schema"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from src.core.config import settings

# Create engine
engine = create_engine(settings.DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

print("=" * 80)
print("CHECKING SPECIFIC REPORT: 3c34a499-9122-4e2b-9033-0d1336e74170")
print("=" * 80)

# Check if report exists
report_id = '3c34a499-9122-4e2b-9033-0d1336e74170'
result = session.execute(text("""
    SELECT id, report_number, title, status, submitted_at, updated_at, deleted_at
    FROM vulnerability_reports 
    WHERE id = :report_id
"""), {"report_id": report_id})

report = result.fetchone()
if report:
    print(f"\n✅ Report FOUND:")
    print(f"   ID: {report[0]}")
    print(f"   Number: {report[1]}")
    print(f"   Title: {report[2]}")
    print(f"   Status: {report[3]}")
    print(f"   Submitted: {report[4]}")
    print(f"   Updated: {report[5]}")
    print(f"   Deleted: {report[6]}")
else:
    print(f"\n❌ Report NOT FOUND in database")

# Check vulnerability_reports table schema
print("\n" + "=" * 80)
print("VULNERABILITY_REPORTS TABLE SCHEMA")
print("=" * 80)

inspector = inspect(engine)
columns = inspector.get_columns('vulnerability_reports')

print("\nColumns in vulnerability_reports table:")
for col in columns:
    nullable = "NULL" if col['nullable'] else "NOT NULL"
    print(f"  - {col['name']:<30} {str(col['type']):<20} {nullable}")

# Check all reports
print("\n" + "=" * 80)
print("ALL REPORTS IN DATABASE")
print("=" * 80)

result = session.execute(text("""
    SELECT id, report_number, title, status, submitted_at, deleted_at
    FROM vulnerability_reports 
    ORDER BY submitted_at DESC
"""))

reports = result.fetchall()
print(f"\nTotal reports: {len(reports)}")
for r in reports:
    deleted = " (DELETED)" if r[5] else ""
    print(f"  - {r[1]}: {r[2][:50]}{deleted}")
    print(f"    ID: {r[0]}")
    print(f"    Status: {r[3]}, Submitted: {r[4]}")

session.close()
