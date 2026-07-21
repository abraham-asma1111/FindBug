#!/usr/bin/env python3
"""
Script to get all valid reports from triage.
Usage: python3 get_valid_reports.py
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from src.core.database import SessionLocal
from src.domain.models.report import VulnerabilityReport
from src.domain.models.researcher import Researcher
from src.domain.models.program import BountyProgram
from src.domain.models.organization import Organization


def get_valid_reports():
    """Get all valid reports from database."""
    db: Session = SessionLocal()
    
    try:
        # Query valid reports with joins
        reports = db.query(
            VulnerabilityReport,
            Researcher.username.label('researcher_name'),
            BountyProgram.name.label('program_name'),
            Organization.company_name.label('organization_name')
        ).join(
            Researcher, VulnerabilityReport.researcher_id == Researcher.id
        ).join(
            BountyProgram, VulnerabilityReport.program_id == BountyProgram.id
        ).join(
            Organization, BountyProgram.organization_id == Organization.id
        ).filter(
            VulnerabilityReport.status == 'valid'
        ).order_by(
            VulnerabilityReport.submitted_at.desc()
        ).all()
        
        print(f"\n{'='*100}")
        print(f"VALID REPORTS FROM TRIAGE ({len(reports)} total)")
        print(f"{'='*100}\n")
        
        if not reports:
            print("No valid reports found.")
            return []
        
        for idx, (report, researcher_name, program_name, org_name) in enumerate(reports, 1):
            print(f"{idx}. Report ID: {report.id}")
            print(f"   Report Number: {report.report_number}")
            print(f"   Title: {report.title}")
            print(f"   Severity: {report.assigned_severity or report.suggested_severity or 'Not assigned'}")
            print(f"   Status: {report.status}")
            print(f"   Researcher: {researcher_name}")
            print(f"   Program: {program_name}")
            print(f"   Organization: {org_name}")
            print(f"   Submitted: {report.submitted_at}")
            print(f"   Updated: {report.updated_at}")
            print(f"   {'-'*98}")
        
        return reports
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return []
    finally:
        db.close()


if __name__ == "__main__":
    reports = get_valid_reports()
    print(f"\nTotal valid reports: {len(reports)}")
