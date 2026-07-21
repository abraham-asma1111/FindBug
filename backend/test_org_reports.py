#!/usr/bin/env python3
"""Test script to check organization reports."""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy.orm import Session
from src.core.database import SessionLocal
from src.domain.models.report import VulnerabilityReport
from src.domain.models.program import BountyProgram
from src.domain.models.organization import Organization
from src.domain.models.user import User

def test_org_reports():
    """Test organization reports query."""
    db: Session = SessionLocal()
    
    try:
        # Find organization user
        org_user = db.query(User).filter(User.email == "org@test.com").first()
        
        if not org_user:
            print("❌ Organization user not found")
            return
        
        print(f"✅ Found organization user: {org_user.email}")
        print(f"   Organization ID: {org_user.organization.id if org_user.organization else 'None'}")
        
        if not org_user.organization:
            print("❌ User has no organization profile")
            return
        
        org_id = org_user.organization.id
        
        # Get organization programs
        programs = db.query(BountyProgram).filter(
            BountyProgram.organization_id == org_id,
            BountyProgram.deleted_at.is_(None)
        ).all()
        
        print(f"\n📋 Organization Programs: {len(programs)}")
        for prog in programs:
            print(f"   - {prog.name} (ID: {prog.id}, Status: {prog.status})")
        
        if not programs:
            print("❌ No programs found for organization")
            return
        
        program_ids = [p.id for p in programs]
        
        # Get all reports for these programs
        reports = db.query(VulnerabilityReport).filter(
            VulnerabilityReport.program_id.in_(program_ids)
        ).all()
        
        print(f"\n📝 Total Reports: {len(reports)}")
        
        if reports:
            print("\nReport Details:")
            for report in reports:
                print(f"   - {report.title}")
                print(f"     ID: {report.id}")
                print(f"     Program ID: {report.program_id}")
                print(f"     Status: {report.status}")
                print(f"     Submitted: {report.submitted_at}")
                print()
        else:
            print("❌ No reports found")
            
            # Check if there are ANY reports in the database
            all_reports = db.query(VulnerabilityReport).all()
            print(f"\n🔍 Total reports in database: {len(all_reports)}")
            
            if all_reports:
                print("\nAll reports program IDs:")
                for r in all_reports:
                    print(f"   - Report: {r.title}, Program ID: {r.program_id}")
                
                print(f"\nOrganization program IDs: {program_ids}")
                
    finally:
        db.close()

if __name__ == "__main__":
    test_org_reports()
