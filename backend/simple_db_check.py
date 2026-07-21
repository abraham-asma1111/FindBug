"""Simple database check."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import text
from src.core.database import SessionLocal

db = SessionLocal()

print("=" * 60)
print("DATABASE QUICK CHECK")
print("=" * 60)

# Check reports
result = db.execute(text("SELECT COUNT(*) FROM vulnerability_reports")).scalar()
print(f"\n🐛 Vulnerability Reports: {result}")

if result > 0:
    # Check by status
    statuses = db.execute(text("""
        SELECT status, COUNT(*) as count 
        FROM vulnerability_reports 
        GROUP BY status
    """)).fetchall()
    print("\n   By Status:")
    for status, count in statuses:
        print(f"   • {status}: {count}")
    
    # Check by severity
    severities = db.execute(text("""
        SELECT assigned_severity, COUNT(*) as count 
        FROM vulnerability_reports 
        WHERE assigned_severity IS NOT NULL
        GROUP BY assigned_severity
    """)).fetchall()
    if severities:
        print("\n   By Severity:")
        for severity, count in severities:
            print(f"   • {severity}: {count}")

# Check users
result = db.execute(text("SELECT COUNT(*) FROM users")).scalar()
print(f"\n👥 Users: {result}")

if result > 0:
    roles = db.execute(text("""
        SELECT role, COUNT(*) as count 
        FROM users 
        GROUP BY role
    """)).fetchall()
    print("\n   By Role:")
    for role, count in roles:
        print(f"   • {role}: {count}")

# Check programs
result = db.execute(text("SELECT COUNT(*) FROM bounty_programs")).scalar()
print(f"\n📋 Bounty Programs: {result}")

# Check organizations
result = db.execute(text("SELECT COUNT(*) FROM organizations")).scalar()
print(f"\n🏢 Organizations: {result}")

print("\n" + "=" * 60)

db.close()
