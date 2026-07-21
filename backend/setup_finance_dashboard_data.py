"""
Setup Finance Dashboard Data
Populates the database with sample data for testing the finance dashboard.
"""
import sys
from pathlib import Path
from decimal import Decimal
from datetime import datetime, timedelta
from uuid import uuid4

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.orm import Session
from src.core.database import SessionLocal, engine
from src.domain.models.user import User
from src.domain.models.researcher import Researcher
from src.domain.models.organization import Organization
from src.domain.models.program import BountyProgram
from src.domain.models.report import VulnerabilityReport


def create_sample_data():
    """Create sample data for finance dashboard."""
    db = SessionLocal()
    
    try:
        print("🚀 Setting up Finance Dashboard Data...")
        
        # Check if we already have data
        existing_reports = db.query(VulnerabilityReport).count()
        if existing_reports > 0:
            print(f"✅ Database already has {existing_reports} reports")
            response = input("Do you want to add more sample data? (y/n): ")
            if response.lower() != 'y':
                print("Skipping data creation")
                return
        
        # Create organization user
        org_user = db.query(User).filter(User.email == "testorg@example.com").first()
        if not org_user:
            org_user = User(
                id=uuid4(),
                email="testorg@example.com",
                full_name="Test Organization",
                role="organization",
                is_active=True,
                email_verified=True
            )
            org_user.set_password("password123")
            db.add(org_user)
            db.flush()
            
            # Create organization profile
            organization = Organization(
                id=uuid4(),
                user_id=org_user.id,
                company_name="Test Security Corp",
                industry="Technology",
                company_size="51-200"
            )
            db.add(organization)
            db.flush()
            print(f"✅ Created organization: {organization.company_name}")
        else:
            organization = org_user.organization
            print(f"✅ Using existing organization: {organization.company_name}")
        
        # Create researchers
        researchers = []
        for i in range(5):
            researcher_user = db.query(User).filter(User.email == f"researcher{i}@example.com").first()
            if not researcher_user:
                researcher_user = User(
                    id=uuid4(),
                    email=f"researcher{i}@example.com",
                    full_name=f"Researcher {i+1}",
                    role="researcher",
                    is_active=True,
                    email_verified=True
                )
                researcher_user.set_password("password123")
                db.add(researcher_user)
                db.flush()
                
                researcher = Researcher(
                    id=uuid4(),
                    user_id=researcher_user.id,
                    username=f"researcher_{i+1}",
                    bio=f"Security researcher #{i+1}",
                    reputation_score=Decimal(str(1000 + (i * 200))),
                    total_earnings=Decimal('0'),
                    rank=i + 1
                )
                db.add(researcher)
                db.flush()
                researchers.append(researcher)
                print(f"✅ Created researcher: {researcher.username}")
            else:
                researchers.append(researcher_user.researcher)
        
        # Create bounty programs
        programs = []
        program_names = [
            "Web Application Security",
            "Mobile App Security",
            "API Security Testing",
            "Infrastructure Security"
        ]
        
        for name in program_names:
            program = db.query(BountyProgram).filter(
                BountyProgram.name == name,
                BountyProgram.organization_id == organization.id
            ).first()
            
            if not program:
                program = BountyProgram(
                    id=uuid4(),
                    organization_id=organization.id,
                    name=name,
                    description=f"Bug bounty program for {name.lower()}",
                    status="public",
                    program_type="bug_bounty",
                    reward_range_min=Decimal('100'),
                    reward_range_max=Decimal('10000')
                )
                db.add(program)
                db.flush()
                programs.append(program)
                print(f"✅ Created program: {program.name}")
            else:
                programs.append(program)
        
        # Create vulnerability reports with bounties
        severities = ['critical', 'high', 'medium', 'low']
        statuses = ['valid', 'resolved']
        bounty_amounts = {
            'critical': [5000, 7500, 10000],
            'high': [2500, 3500, 5000],
            'medium': [1000, 1500, 2000],
            'low': [250, 500, 750]
        }
        
        reports_created = 0
        total_paid = Decimal('0')
        total_pending = Decimal('0')
        
        # Create reports over the last 6 months
        for month_ago in range(6):
            month_date = datetime.utcnow() - timedelta(days=30 * month_ago)
            reports_this_month = 10 + (month_ago * 2)  # More recent months have more reports
            
            for i in range(reports_this_month):
                researcher = researchers[i % len(researchers)]
                program = programs[i % len(programs)]
                severity = severities[i % len(severities)]
                status = statuses[i % len(statuses)]
                
                # Random bounty amount based on severity
                import random
                bounty_amount = Decimal(str(random.choice(bounty_amounts[severity])))
                
                report = VulnerabilityReport(
                    id=uuid4(),
                    program_id=program.id,
                    researcher_id=researcher.id,
                    report_number=f"VR-{reports_created + 1:05d}",
                    title=f"{severity.capitalize()} vulnerability in {program.name}",
                    description=f"Sample {severity} vulnerability report",
                    vulnerability_type="xss" if i % 2 == 0 else "sql_injection",
                    suggested_severity=severity,
                    assigned_severity=severity,
                    status=status,
                    bounty_amount=bounty_amount,
                    bounty_status='paid' if status == 'resolved' else 'approved',
                    submitted_at=month_date - timedelta(days=random.randint(0, 28)),
                    triaged_at=month_date - timedelta(days=random.randint(0, 27)),
                    bounty_approved_at=month_date - timedelta(days=random.randint(0, 26))
                )
                db.add(report)
                
                if report.bounty_status == 'paid':
                    total_paid += bounty_amount
                    # Update researcher earnings
                    researcher.total_earnings = (researcher.total_earnings or Decimal('0')) + bounty_amount
                else:
                    total_pending += bounty_amount
                
                reports_created += 1
        
        db.commit()
        
        # Calculate platform revenue (30% commission)
        platform_revenue = total_paid * Decimal('0.30')
        
        print("\n" + "="*60)
        print("✅ Finance Dashboard Data Created Successfully!")
        print("="*60)
        print(f"📊 Reports Created: {reports_created}")
        print(f"💰 Total Paid Out: ${total_paid:,.2f}")
        print(f"⏳ Total Pending: ${total_pending:,.2f}")
        print(f"🏦 Platform Revenue (30%): ${platform_revenue:,.2f}")
        print(f"👥 Researchers: {len(researchers)}")
        print(f"📋 Programs: {len(programs)}")
        print("="*60)
        print("\n🎉 You can now refresh the Finance Dashboard to see the data!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    create_sample_data()
