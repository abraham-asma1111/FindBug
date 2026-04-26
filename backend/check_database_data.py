"""
Check what data exists in the database.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.orm import Session
from src.core.database import SessionLocal
from src.domain.models.user import User
from src.domain.models.organization import Organization
from src.domain.models.program import BountyProgram
from src.domain.models.report import VulnerabilityReport
from src.domain.models.researcher import Researcher


def check_database():
    """Check what data exists in the database."""
    db: Session = SessionLocal()
    
    try:
        print("=" * 60)
        print("DATABASE DATA ANALYSIS")
        print("=" * 60)
        
        # Check Users
        total_users = db.query(User).count()
        researchers = db.query(User).filter(User.role == 'researcher').count()
        organizations = db.query(User).filter(User.role == 'organization').count()
        triage_specialists = db.query(User).filter(User.role == 'triage_specialist').count()
        admins = db.query(User).filter(User.role == 'admin').count()
        
        print(f"\n👥 USERS: {total_users} total")
        print(f"   - Researchers: {researchers}")
        print(f"   - Organizations: {organizations}")
        print(f"   - Triage Specialists: {triage_specialists}")
        print(f"   - Admins: {admins}")
        
        if total_users > 0:
            print("\n   Sample users:")
            sample_users = db.query(User).limit(5).all()
            for user in sample_users:
                print(f"   • {user.email} ({user.role})")
        
        # Check Organizations
        total_orgs = db.query(Organization).count()
        print(f"\n🏢 ORGANIZATIONS: {total_orgs} total")
        
        if total_orgs > 0:
            orgs = db.query(Organization).limit(5).all()
            for org in orgs:
                print(f"   • {org.name} ({org.email})")
        
        # Check Bug Bounty Programs
        total_programs = db.query(BountyProgram).count()
        active_programs = db.query(BountyProgram).filter(
            BountyProgram.status == 'active'
        ).count()
        
        print(f"\n📋 BUG BOUNTY PROGRAMS: {total_programs} total")
        print(f"   - Active: {active_programs}")
        
        if total_programs > 0:
            programs = db.query(BountyProgram).limit(5).all()
            for program in programs:
                print(f"   • {program.name} ({program.status})")
        
        # Check Vulnerability Reports
        total_reports = db.query(VulnerabilityReport).count()
        
        print(f"\n🐛 VULNERABILITY REPORTS: {total_reports} total")
        
        if total_reports > 0:
            # Count by status
            statuses = ['new', 'triaged', 'valid', 'invalid', 'duplicate', 'resolved']
            print("   By Status:")
            for status in statuses:
                count = db.query(VulnerabilityReport).filter(
                    VulnerabilityReport.status == status
                ).count()
                if count > 0:
                    print(f"   • {status}: {count}")
            
            # Count by severity
            severities = ['critical', 'high', 'medium', 'low']
            print("\n   By Severity:")
            for severity in severities:
                count = db.query(VulnerabilityReport).filter(
                    VulnerabilityReport.assigned_severity == severity
                ).count()
                if count > 0:
                    print(f"   • {severity}: {count}")
            
            # Sample reports
            print("\n   Sample reports:")
            sample_reports = db.query(VulnerabilityReport).limit(5).all()
            for report in sample_reports:
                print(f"   • {report.report_number}: {report.title[:50]}... ({report.status})")
        
        # Check Researcher Profiles
        total_researcher_profiles = db.query(Researcher).count()
        print(f"\n🔬 RESEARCHER PROFILES: {total_researcher_profiles} total")
        
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        
        if total_reports == 0:
            print("\n❌ NO VULNERABILITY REPORTS FOUND")
            print("   The triage analytics page will show 'No analytics data available'")
            print("\n💡 TO FIX THIS:")
            print("   1. Run: python backend/populate_triage_data.py")
            print("   2. Or submit reports through the researcher portal")
        elif total_reports < 10:
            print(f"\n⚠️  ONLY {total_reports} REPORTS FOUND")
            print("   Analytics will show limited data")
            print("\n💡 TO ADD MORE DATA:")
            print("   Run: python backend/populate_triage_data.py")
        else:
            print(f"\n✅ DATABASE HAS SUFFICIENT DATA ({total_reports} reports)")
            print("   Triage analytics should display properly")
            print("\n🎯 Access the analytics at:")
            print("   http://localhost:3000/triage/analytics")
            
            # Find triage specialist
            triage_user = db.query(User).filter(
                User.role == 'triage_specialist'
            ).first()
            
            if triage_user:
                print(f"\n🔐 Login as triage specialist:")
                print(f"   Email: {triage_user.email}")
                print(f"   (You'll need to know the password)")
            else:
                print("\n⚠️  No triage specialist user found")
                print("   Create one with: python backend/create_triage_user.py")
        
        print("\n" + "=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error checking database: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    check_database()
