#!/usr/bin/env python3
"""Debug script to investigate why reports are failing to load."""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from src.core.config import settings

# Create database connection
engine = create_engine(settings.DATABASE_URL)
Session = sessionmaker(bind=engine)
db = Session()

print("=" * 80)
print("REPORT LOADING DEBUG")
print("=" * 80)

# 1. Get all reports
print("\n1. ALL VULNERABILITY REPORTS:")
reports_query = text("""
    SELECT 
        id, report_number, title, status, 
        assigned_severity, suggested_severity,
        program_id, researcher_id,
        submitted_at, created_at
    FROM vulnerability_reports
    WHERE deleted_at IS NULL
    ORDER BY submitted_at DESC
""")
reports = db.execute(reports_query).fetchall()

print(f"   Found {len(reports)} active reports:")
for report in reports:
    print(f"\n   Report: {report.report_number}")
    print(f"   - ID: {report.id}")
    print(f"   - Title: {report.title}")
    print(f"   - Status: {report.status}")
    print(f"   - Severity: {report.assigned_severity or report.suggested_severity}")
    print(f"   - Program ID: {report.program_id}")
    print(f"   - Researcher ID: {report.researcher_id}")
    print(f"   - Submitted: {report.submitted_at}")

# 2. Check if programs exist for these reports
print("\n2. CHECKING PROGRAM REFERENCES:")
program_ids = set([r.program_id for r in reports if r.program_id])
for program_id in program_ids:
    program_query = text("""
        SELECT id, name, status, organization_id
        FROM bounty_programs
        WHERE id = :program_id
    """)
    program = db.execute(program_query, {"program_id": program_id}).fetchone()
    if program:
        print(f"   ✅ Program {program_id}: {program.name} (status: {program.status})")
    else:
        print(f"   ❌ Program {program_id}: NOT FOUND")

# 3. Check if researchers exist for these reports
print("\n3. CHECKING RESEARCHER REFERENCES:")
researcher_ids = set([r.researcher_id for r in reports if r.researcher_id])
for researcher_id in researcher_ids:
    researcher_query = text("""
        SELECT r.id, r.username, u.email
        FROM researchers r
        LEFT JOIN users u ON r.user_id = u.id
        WHERE r.id = :researcher_id
    """)
    researcher = db.execute(researcher_query, {"researcher_id": researcher_id}).fetchone()
    if researcher:
        print(f"   ✅ Researcher {researcher_id}: {researcher.username or researcher.email}")
    else:
        print(f"   ❌ Researcher {researcher_id}: NOT FOUND")

# 4. Check report attachments
print("\n4. CHECKING REPORT ATTACHMENTS:")
attachments_query = text("""
    SELECT report_id, COUNT(*) as count
    FROM report_attachments
    GROUP BY report_id
""")
attachments = db.execute(attachments_query).fetchall()
if attachments:
    print(f"   Found attachments for {len(attachments)} reports:")
    for att in attachments:
        print(f"   - Report {att.report_id}: {att.count} attachments")
else:
    print("   No attachments found")

# 5. Check report comments
print("\n5. CHECKING REPORT COMMENTS:")
comments_query = text("""
    SELECT report_id, COUNT(*) as count
    FROM report_comments
    GROUP BY report_id
""")
comments = db.execute(comments_query).fetchall()
if comments:
    print(f"   Found comments for {len(comments)} reports:")
    for comm in comments:
        print(f"   - Report {comm.report_id}: {comm.count} comments")
else:
    print("   No comments found")

# 6. Test fetching a specific report (the one from the error log)
print("\n6. TESTING SPECIFIC REPORT FETCH:")
test_report_id = "3c34a499-9122-4e2b-9033-0d1336e74170"
test_query = text("""
    SELECT 
        vr.*,
        bp.name as program_name,
        r.username as researcher_username
    FROM vulnerability_reports vr
    LEFT JOIN bounty_programs bp ON vr.program_id = bp.id
    LEFT JOIN researchers r ON vr.researcher_id = r.id
    WHERE vr.id = :report_id
""")
test_report = db.execute(test_query, {"report_id": test_report_id}).fetchone()

if test_report:
    print(f"   ✅ Report {test_report_id} found:")
    print(f"   - Title: {test_report.title}")
    print(f"   - Status: {test_report.status}")
    print(f"   - Program: {test_report.program_name}")
    print(f"   - Researcher: {test_report.researcher_username}")
else:
    print(f"   ❌ Report {test_report_id} NOT FOUND")

# 7. Check for any database constraints or issues
print("\n7. DATABASE INTEGRITY CHECK:")
orphaned_reports_query = text("""
    SELECT vr.id, vr.report_number, vr.program_id
    FROM vulnerability_reports vr
    LEFT JOIN bounty_programs bp ON vr.program_id = bp.id
    WHERE vr.deleted_at IS NULL AND bp.id IS NULL
""")
orphaned_reports = db.execute(orphaned_reports_query).fetchall()

if orphaned_reports:
    print(f"   ⚠️  Found {len(orphaned_reports)} reports with missing programs:")
    for rep in orphaned_reports:
        print(f"   - {rep.report_number} (program_id: {rep.program_id})")
else:
    print("   ✅ All reports have valid program references")

print("\n" + "=" * 80)
print("SUMMARY:")
print("=" * 80)
print(f"Total active reports: {len(reports)}")
print(f"Total programs referenced: {len(program_ids)}")
print(f"Total researchers referenced: {len(researcher_ids)}")
print(f"Reports with attachments: {len(attachments) if attachments else 0}")
print(f"Reports with comments: {len(comments) if comments else 0}")
print(f"Orphaned reports: {len(orphaned_reports) if orphaned_reports else 0}")
print("=" * 80)

db.close()
