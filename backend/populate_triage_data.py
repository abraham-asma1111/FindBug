"""
Populate database with sample triage data for testing analytics.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from datetime import datetime, timedelta
from decimal import Decimal
from uuid import uuid4
import random

from sqlalchemy.orm import Session
from src.core.database import SessionLocal
from src.domain.models.user import User
from src.domain.models.organization import Organization
from src.domain.models.program import BountyProgram
from src.domain.models.report import VulnerabilityReport
from src.domain.models.researcher import Researcher


def create_sample_data():
    """Create sample triage data."""
    db: Session = SessionLocal()
    
    try:
        print("🔍 Checking existing data...")
        
        # Check if we already have data
        existing_reports = db.query(VulnerabilityReport).count()
        if existing_reports > 0:
            print(f"✅ Database already has {existing_reports} reports")
            response = input("Do you want to add more sample data? (y/n): ")
            if response.lower() != 'y':
                print("Skipping data population")
                return
        
        # Get or create organization
        org = db.query(Organization).first()
        if not org:
            print("📦 Creating organization...")
            org = Organization(
                id=uuid4(),
                name="TechCorp Security",
                email="security@techcorp.com",
                is_verified=True
            )
            db.add(org)
            db.commit()
            db.refresh(org)
        
        # Get or create programs
        programs = db.query(BountyProgram).filter(
            BountyProgram.organization_id == org.id
        ).all()
        
        if not programs:
            print("📋 Creating bug bounty programs...")
            program_names = [
                "Web Application Security",
                "Mobile App Testing",
                "API Security",
                "Cloud Infrastructure",
                "IoT Devices"
            ]
            
            programs = []
            for name in program_names:
                program = BountyProgram(
                    id=uuid4(),
                    organization_id=org.id,
                    name=name,
                    description=f"Security testing for {name}",
                    status="active",
                    is_public=True
                )
                db.add(program)
                programs.append(program)
            
            db.commit()
            for p in programs:
                db.refresh(p)
        
        # Get or create researchers
        researchers = db.query(User).filter(User.role == 'researcher').all()
        
        if len(researchers) < 5:
            print("👥 Creating researcher users...")
            researcher_emails = [
                "jamie.dixon@example.com",
                "alex.rivera@example.com",
                "sam.chen@example.com",
                "taylor.kim@example.com",
                "jordan.lee@example.com"
            ]
            
            researchers = []
            for email in researcher_emails:
                existing = db.query(User).filter(User.email == email).first()
                if existing:
                    researchers.append(existing)
                    continue
                
                user = User(
                    id=uuid4(),
                    email=email,
                    username=email.split('@')[0],
                    hashed_password="$2b$12$dummy_hash_for_testing",
                    role="researcher",
                    is_active=True,
                    is_verified=True
                )
                db.add(user)
                researchers.append(user)
                
                # Create researcher profile
                researcher_profile = Researcher(
                    id=uuid4(),
                    user_id=user.id,
                    reputation_score=random.randint(50, 100)
                )
                db.add(researcher_profile)
            
            db.commit()
            for r in researchers:
                db.refresh(r)
        
        # Get or create triage specialist
        triage_user = db.query(User).filter(User.role == 'triage_specialist').first()
        if not triage_user:
            print("🔍 Creating triage specialist...")
            triage_user = User(
                id=uuid4(),
                email="triage@techcorp.com",
                username="triage_specialist",
                hashed_password="$2b$12$dummy_hash_for_testing",
                role="triage_specialist",
                is_active=True,
                is_verified=True
            )
            db.add(triage_user)
            db.commit()
            db.refresh(triage_user)
        
        print("📊 Creating vulnerability reports...")
        
        # Create reports with various statuses and severities
        statuses = ['new', 'triaged', 'valid', 'invalid', 'duplicate', 'resolved']
        severities = ['critical', 'high', 'medium', 'low']
        
        # Distribution weights for more realistic data
        status_weights = [15, 10, 30, 8, 5, 12]  # More valid reports
        severity_weights = [5, 20, 35, 40]  # More medium/low severity
        
        reports_created = 0
        
        for i in range(80):
            researcher = random.choice(researchers)
            program = random.choice(programs)
            status = random.choices(statuses, weights=status_weights)[0]
            severity = random.choices(severities, weights=severity_weights)[0]
            
            # Create report with dates in the past 30 days
            days_ago = random.randint(0, 30)
            submitted_at = datetime.utcnow() - timedelta(days=days_ago)
            
            report = VulnerabilityReport(
                id=uuid4(),
                report_number=f"VUL-{4000 + i}",
                program_id=program.id,
                researcher_id=researcher.id,
                title=f"Security vulnerability in {program.name} - {i+1}",
                description=f"Detailed description of vulnerability {i+1}",
                status=status,
                suggested_severity=severity,
                assigned_severity=severity if status in ['triaged', 'valid', 'invalid', 'resolved'] else None,
                submitted_at=submitted_at,
                last_activity_at=submitted_at
            )
            
            # Add triage information for processed reports
            if status in ['triaged', 'valid', 'invalid', 'duplicate', 'resolved']:
                triage_hours = random.uniform(0.5, 5.0)
                report.triaged_at = submitted_at + timedelta(hours=triage_hours)
                report.triaged_by = triage_user.id
                report.last_activity_at = report.triaged_at
                
                # Add CVSS score for valid reports
                if status == 'valid':
                    if severity == 'critical':
                        report.cvss_score = Decimal(str(random.uniform(9.0, 10.0)))
                    elif severity == 'high':
                        report.cvss_score = Decimal(str(random.uniform(7.0, 8.9)))
                    elif severity == 'medium':
                        report.cvss_score = Decimal(str(random.uniform(4.0, 6.9)))
                    else:
                        report.cvss_score = Decimal(str(random.uniform(0.1, 3.9)))
            
            db.add(report)
            reports_created += 1
            
            if reports_created % 20 == 0:
                print(f"  Created {reports_created} reports...")
        
        db.commit()
        
        print(f"\n✅ Successfully created {reports_created} vulnerability reports!")
        print(f"📊 Distribution:")
        print(f"   - Organizations: 1")
        print(f"   - Programs: {len(programs)}")
        print(f"   - Researchers: {len(researchers)}")
        print(f"   - Reports: {reports_created}")
        print(f"\n🎯 You can now view the triage analytics at: http://localhost:3000/triage/analytics")
        print(f"   Login as: triage@techcorp.com")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("🚀 Populating triage data...")
    create_sample_data()
    print("✨ Done!")
