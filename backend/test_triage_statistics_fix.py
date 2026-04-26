"""Test script to create correct triage statistics endpoint."""
import psycopg2
from datetime import datetime, timedelta

conn = psycopg2.connect(
    dbname='bug_bounty_production',
    user='bugbounty_user',
    password='changeme123',
    host='localhost',
    port='5432'
)
cur = conn.cursor()

print("=" * 80)
print("REAL DATABASE STATISTICS")
print("=" * 80)

# Total reports
cur.execute("SELECT COUNT(*) FROM vulnerability_reports")
total_reports = cur.fetchone()[0]
print(f"\n✓ Total Reports: {total_reports}")

# Pending triage (status = 'new' or 'triaged')
cur.execute("SELECT COUNT(*) FROM vulnerability_reports WHERE status IN ('new', 'triaged')")
pending_triage = cur.fetchone()[0]
print(f"✓ Pending Triage: {pending_triage}")

# Status breakdown
cur.execute("""
    SELECT 
        COALESCE(SUM(CASE WHEN status = 'new' THEN 1 ELSE 0 END), 0) as new,
        COALESCE(SUM(CASE WHEN status = 'triaged' THEN 1 ELSE 0 END), 0) as triaged,
        COALESCE(SUM(CASE WHEN status = 'valid' THEN 1 ELSE 0 END), 0) as valid,
        COALESCE(SUM(CASE WHEN status = 'invalid' THEN 1 ELSE 0 END), 0) as invalid,
        COALESCE(SUM(CASE WHEN status = 'duplicate' THEN 1 ELSE 0 END), 0) as duplicate,
        COALESCE(SUM(CASE WHEN status = 'resolved' THEN 1 ELSE 0 END), 0) as resolved
    FROM vulnerability_reports
""")
status_row = cur.fetchone()
print(f"\n✓ Status Breakdown:")
print(f"  - new: {status_row[0]}")
print(f"  - triaged: {status_row[1]}")
print(f"  - valid: {status_row[2]}")
print(f"  - invalid: {status_row[3]}")
print(f"  - duplicate: {status_row[4]}")
print(f"  - resolved: {status_row[5]}")

# Severity breakdown
cur.execute("""
    SELECT 
        COALESCE(SUM(CASE WHEN COALESCE(assigned_severity, suggested_severity) = 'critical' THEN 1 ELSE 0 END), 0) as critical,
        COALESCE(SUM(CASE WHEN COALESCE(assigned_severity, suggested_severity) = 'high' THEN 1 ELSE 0 END), 0) as high,
        COALESCE(SUM(CASE WHEN COALESCE(assigned_severity, suggested_severity) = 'medium' THEN 1 ELSE 0 END), 0) as medium,
        COALESCE(SUM(CASE WHEN COALESCE(assigned_severity, suggested_severity) = 'low' THEN 1 ELSE 0 END), 0) as low,
        COALESCE(SUM(CASE WHEN COALESCE(assigned_severity, suggested_severity) = 'info' THEN 1 ELSE 0 END), 0) as info
    FROM vulnerability_reports
""")
severity_row = cur.fetchone()
print(f"\n✓ Severity Breakdown:")
print(f"  - critical: {severity_row[0]}")
print(f"  - high: {severity_row[1]}")
print(f"  - medium: {severity_row[2]}")
print(f"  - low: {severity_row[3]}")
print(f"  - info: {severity_row[4]}")

# Top researchers
cur.execute("""
    SELECT 
        r.id,
        u.email,
        COUNT(vr.id) as total_reports,
        SUM(CASE WHEN vr.status = 'valid' THEN 1 ELSE 0 END) as valid_reports
    FROM researchers r
    JOIN users u ON r.user_id = u.id
    LEFT JOIN vulnerability_reports vr ON vr.researcher_id = r.id
    GROUP BY r.id, u.email
    HAVING COUNT(vr.id) > 0
    ORDER BY COUNT(vr.id) DESC
    LIMIT 5
""")
print(f"\n✓ Top Researchers:")
for row in cur.fetchall():
    print(f"  - {row[1]}: {row[2]} reports ({row[3]} valid)")

# Top programs
cur.execute("""
    SELECT 
        bp.id,
        bp.name,
        COUNT(vr.id) as total_reports,
        SUM(CASE WHEN vr.status IN ('new', 'triaged') THEN 1 ELSE 0 END) as pending_count
    FROM bounty_programs bp
    LEFT JOIN vulnerability_reports vr ON vr.program_id = bp.id
    GROUP BY bp.id, bp.name
    HAVING COUNT(vr.id) > 0
    ORDER BY SUM(CASE WHEN vr.status IN ('new', 'triaged') THEN 1 ELSE 0 END) DESC
    LIMIT 5
""")
print(f"\n✓ Top Programs:")
for row in cur.fetchall():
    print(f"  - {row[1]}: {row[2]} total, {row[3]} pending")

print("\n" + "=" * 80)
print("✅ ALL DATA IS REAL FROM DATABASE")
print("=" * 80)

cur.close()
conn.close()
