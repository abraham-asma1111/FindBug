#!/usr/bin/env python3
"""Check all PTaaS findings/reports in database"""
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
print("PTAAS FINDINGS TABLE SCHEMA")
print("=" * 80)

inspector = inspect(engine)
columns = inspector.get_columns('ptaas_findings')

print("\nColumns in ptaas_findings table:")
for col in columns:
    nullable = "NULL" if col['nullable'] else "NOT NULL"
    print(f"  - {col['name']:<30} {str(col['type']):<20} {nullable}")

# Check all PTaaS findings
print("\n" + "=" * 80)
print("ALL PTAAS FINDINGS IN DATABASE")
print("=" * 80)

result = session.execute(text("""
    SELECT 
        id, 
        title, 
        severity, 
        status, 
        discovered_at,
        engagement_id,
        discovered_by
    FROM ptaas_findings 
    ORDER BY discovered_at DESC
"""))

findings = result.fetchall()
print(f"\nTotal PTaaS findings: {len(findings)}")

if len(findings) == 0:
    print("  ❌ No PTaaS findings found in database")
else:
    for f in findings:
        print(f"\n  Finding ID: {f[0]}")
        print(f"    Title: {f[1]}")
        print(f"    Severity: {f[2]}")
        print(f"    Status: {f[3]}")
        print(f"    Discovered: {f[4]}")
        print(f"    Engagement: {f[5]}")
        print(f"    Discovered by: {f[6]}")

# Check PTaaS engagements
print("\n" + "=" * 80)
print("ALL PTAAS ENGAGEMENTS IN DATABASE")
print("=" * 80)

result = session.execute(text("""
    SELECT 
        id, 
        name, 
        status, 
        testing_type,
        start_date,
        end_date,
        organization_id
    FROM ptaas_engagements 
    ORDER BY start_date DESC
"""))

engagements = result.fetchall()
print(f"\nTotal PTaaS engagements: {len(engagements)}")

if len(engagements) == 0:
    print("  ❌ No PTaaS engagements found in database")
else:
    for e in engagements:
        print(f"\n  Engagement ID: {e[0]}")
        print(f"    Name: {e[1]}")
        print(f"    Status: {e[2]}")
        print(f"    Type: {e[3]}")
        print(f"    Start: {e[4]}")
        print(f"    End: {e[5]}")
        print(f"    Organization: {e[6]}")

session.close()

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"✓ PTaaS Engagements: {len(engagements)}")
print(f"✓ PTaaS Findings: {len(findings)}")
print(f"\nNote: PTaaS findings table has 'discovered_at' column (not 'created_at')")
print("      Frontend expects 'created_at' field in API response")
