"""
Check if the problematic ID exists in both vulnerability_reports and ptaas_findings tables
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

report_id = '3c34a499-9122-4e2b-9033-0d1336e74170'

print("=" * 80)
print(f"CHECKING ID: {report_id}")
print("=" * 80)

# Check in vulnerability_reports
print("\n1. CHECKING IN vulnerability_reports TABLE:")
result = session.execute(text("""
    SELECT id, report_number, title, status, submitted_at
    FROM vulnerability_reports
    WHERE id = :report_id
"""), {"report_id": report_id})

vuln_report = result.fetchone()
if vuln_report:
    print(f"  ✓ FOUND in vulnerability_reports:")
    print(f"    ID: {vuln_report[0]}")
    print(f"    Report Number: {vuln_report[1]}")
    print(f"    Title: {vuln_report[2]}")
    print(f"    Status: {vuln_report[3]}")
    print(f"    Submitted: {vuln_report[4]}")
else:
    print(f"  ✗ NOT FOUND in vulnerability_reports")

# Check in ptaas_findings
print("\n2. CHECKING IN ptaas_findings TABLE:")
result = session.execute(text("""
    SELECT id, title, severity, status, discovered_at, engagement_id
    FROM ptaas_findings
    WHERE id = :report_id
"""), {"report_id": report_id})

ptaas_finding = result.fetchone()
if ptaas_finding:
    print(f"  ✓ FOUND in ptaas_findings:")
    print(f"    ID: {ptaas_finding[0]}")
    print(f"    Title: {ptaas_finding[1]}")
    print(f"    Severity: {ptaas_finding[2]}")
    print(f"    Status: {ptaas_finding[3]}")
    print(f"    Discovered: {ptaas_finding[4]}")
    print(f"    Engagement ID: {ptaas_finding[5]}")
else:
    print(f"  ✗ NOT FOUND in ptaas_findings")

print("\n" + "=" * 80)
print("CONCLUSION:")
print("=" * 80)

if vuln_report and ptaas_finding:
    print("⚠️  ID EXISTS IN BOTH TABLES - This is a data integrity issue!")
elif vuln_report:
    print("✓ ID only exists in vulnerability_reports (correct)")
elif ptaas_finding:
    print("✓ ID only exists in ptaas_findings (correct)")
    print("\n⚠️  PROBLEM: Frontend is trying to load this PTaaS finding as a vulnerability report!")
    print("   The dashboard or report list is incorrectly routing PTaaS findings to /researcher/reports/{id}")
else:
    print("✗ ID doesn't exist in either table")

session.close()
