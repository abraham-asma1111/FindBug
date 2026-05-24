#!/usr/bin/env python3
"""
Test script to verify Finance Dashboard data is available in the database.
Run this to check if the backend will return data correctly.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from src.domain.models.bounty_payment import BountyPayment
from src.domain.models.report import VulnerabilityReport
from src.domain.models.program import BountyProgram
from src.domain.models.researcher import Researcher
from src.domain.models.organization import Organization
from src.core.config import settings

# Create database connection
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

print("=" * 80)
print("FINANCE DASHBOARD DATA VERIFICATION")
print("=" * 80)

# 1. Check Bounty Payments
print("\n1. BOUNTY PAYMENTS:")
print("-" * 80)
total_payments = db.query(BountyPayment).count()
print(f"   Total payments in database: {total_payments}")

if total_payments > 0:
    # Payments by status
    for status in ['completed', 'approved', 'processing', 'pending']:
        count = db.query(BountyPayment).filter(BountyPayment.status == status).count()
        if count > 0:
            print(f"   - {status}: {count}")
    
    # Total amounts
    total_paid = db.query(func.sum(BountyPayment.researcher_amount)).filter(
        BountyPayment.status.in_(['completed', 'approved'])
    ).scalar() or 0
    
    total_pending = db.query(func.sum(BountyPayment.researcher_amount)).filter(
        BountyPayment.status == 'pending'
    ).scalar() or 0
    
    total_revenue = db.query(func.sum(BountyPayment.total_amount)).filter(
        BountyPayment.status.in_(['completed', 'approved'])
    ).scalar() or 0
    
    total_commission = db.query(func.sum(BountyPayment.commission_amount)).filter(
        BountyPayment.status.in_(['completed', 'approved'])
    ).scalar() or 0
    
    print(f"\n   Financial Summary:")
    print(f"   - Total Revenue (Platform): ETB {total_revenue:,.2f}")
    print(f"   - Total Paid to Researchers: ETB {total_paid:,.2f}")
    print(f"   - Total Pending Payouts: ETB {total_pending:,.2f}")
    print(f"   - Platform Commission: ETB {total_commission:,.2f}")
    
    # Recent payments
    print(f"\n   Recent Payments (last 5):")
    recent = db.query(BountyPayment).order_by(BountyPayment.created_at.desc()).limit(5).all()
    for p in recent:
        researcher = db.query(Researcher).filter(Researcher.id == p.researcher_id).first()
        researcher_name = researcher.username if researcher else "Unknown"
        print(f"   - {researcher_name}: ETB {p.researcher_amount:,.2f} ({p.status})")
else:
    print("   ⚠️  No payments found in database")

# 2. Check Vulnerability Reports
print("\n2. VULNERABILITY REPORTS:")
print("-" * 80)
total_reports = db.query(VulnerabilityReport).count()
print(f"   Total reports in database: {total_reports}")

if total_reports > 0:
    # Reports by status
    for status in ['new', 'triaged', 'valid', 'invalid', 'resolved']:
        count = db.query(VulnerabilityReport).filter(VulnerabilityReport.status == status).count()
        if count > 0:
            print(f"   - {status}: {count}")
    
    # Reports by severity
    print(f"\n   By Severity:")
    for severity in ['critical', 'high', 'medium', 'low']:
        count = db.query(VulnerabilityReport).filter(
            VulnerabilityReport.assigned_severity == severity
        ).count()
        if count > 0:
            print(f"   - {severity}: {count}")
    
    # Recent reports
    print(f"\n   Recent Reports (last 5):")
    recent = db.query(VulnerabilityReport).order_by(
        VulnerabilityReport.submitted_at.desc()
    ).limit(5).all()
    for r in recent:
        program = db.query(BountyProgram).filter(BountyProgram.id == r.program_id).first()
        program_name = program.name if program else "Unknown"
        print(f"   - {r.title[:50]}... ({program_name}) - {r.status}")
else:
    print("   ⚠️  No reports found in database")

# 3. Check Programs
print("\n3. BOUNTY PROGRAMS:")
print("-" * 80)
total_programs = db.query(BountyProgram).count()
print(f"   Total programs in database: {total_programs}")

if total_programs > 0:
    # Programs with reports
    programs_with_reports = db.query(
        BountyProgram.id,
        BountyProgram.name,
        func.count(VulnerabilityReport.id).label('report_count')
    ).outerjoin(
        VulnerabilityReport, VulnerabilityReport.program_id == BountyProgram.id
    ).group_by(
        BountyProgram.id, BountyProgram.name
    ).having(
        func.count(VulnerabilityReport.id) > 0
    ).order_by(
        func.count(VulnerabilityReport.id).desc()
    ).limit(5).all()
    
    print(f"\n   Top Programs by Reports:")
    for p in programs_with_reports:
        print(f"   - {p.name}: {p.report_count} reports")
else:
    print("   ⚠️  No programs found in database")

# 4. Check Researchers
print("\n4. RESEARCHERS:")
print("-" * 80)
total_researchers = db.query(Researcher).count()
print(f"   Total researchers in database: {total_researchers}")

# 5. Check Organizations
print("\n5. ORGANIZATIONS:")
print("-" * 80)
total_orgs = db.query(Organization).count()
print(f"   Total organizations in database: {total_orgs}")

# Summary
print("\n" + "=" * 80)
print("SUMMARY:")
print("=" * 80)

if total_payments == 0:
    print("❌ NO PAYMENTS FOUND")
    print("   This is why Platform Revenue and Total Paid show $0")
    print("   The database has approved bounties but no payment records yet.")
    print("\n   To fix this, you need to:")
    print("   1. Create payment records for approved bounties")
    print("   2. Or approve and pay some bounties through the system")
else:
    print("✅ PAYMENTS FOUND - Dashboard should show data")

if total_reports == 0:
    print("❌ NO REPORTS FOUND")
else:
    print(f"✅ {total_reports} REPORTS FOUND")

if total_programs == 0:
    print("❌ NO PROGRAMS FOUND")
else:
    print(f"✅ {total_programs} PROGRAMS FOUND")

print("\n" + "=" * 80)
print("NEXT STEPS:")
print("=" * 80)
print("1. Restart the backend server:")
print("   cd backend && python -m uvicorn src.main:app --reload")
print("\n2. Hard refresh the frontend (Ctrl+Shift+R)")
print("\n3. Check the Finance Dashboard at:")
print("   http://localhost:3000/finance/dashboard")
print("=" * 80)

db.close()
