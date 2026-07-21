#!/usr/bin/env python3
"""Check for duplicate reports in the database."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.core.config import settings

# Create database connection
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

print("=" * 80)
print("CHECKING DUPLICATE REPORTS IN DATABASE")
print("=" * 80)

# Check all reports
from src.domain.models.report import VulnerabilityReport

all_reports = db.query(VulnerabilityReport).all()
print(f"\nTotal reports in database: {len(all_reports)}")

# Check for reports marked as duplicates
duplicate_reports = db.query(VulnerabilityReport).filter(
    VulnerabilityReport.is_duplicate == True
).all()

print(f"Reports with is_duplicate=True: {len(duplicate_reports)}")

if duplicate_reports:
    print("\nDuplicate Reports Found:")
    print("-" * 80)
    for report in duplicate_reports:
        print(f"\nReport ID: {report.id}")
        print(f"Report Number: {report.report_number}")
        print(f"Title: {report.title}")
        print(f"Status: {report.status}")
        print(f"is_duplicate: {report.is_duplicate}")
        print(f"duplicate_of: {report.duplicate_of}")
        print(f"duplicate_detected_at: {report.duplicate_detected_at}")
else:
    print("\nNo reports marked as duplicates found.")

# Check for reports with status='duplicate'
status_duplicate = db.query(VulnerabilityReport).filter(
    VulnerabilityReport.status == 'duplicate'
).all()

print(f"\n\nReports with status='duplicate': {len(status_duplicate)}")

if status_duplicate:
    print("\nReports with duplicate status:")
    print("-" * 80)
    for report in status_duplicate:
        print(f"\nReport ID: {report.id}")
        print(f"Report Number: {report.report_number}")
        print(f"Title: {report.title}")
        print(f"Status: {report.status}")
        print(f"is_duplicate: {report.is_duplicate}")
        print(f"duplicate_of: {report.duplicate_of}")

# Show first 5 reports for reference
print("\n\nFirst 5 reports in database:")
print("-" * 80)
for report in all_reports[:5]:
    print(f"\nReport ID: {report.id}")
    print(f"Report Number: {report.report_number}")
    print(f"Title: {report.title}")
    print(f"Status: {report.status}")
    print(f"is_duplicate: {report.is_duplicate}")
    print(f"duplicate_of: {report.duplicate_of}")

db.close()
print("\n" + "=" * 80)
