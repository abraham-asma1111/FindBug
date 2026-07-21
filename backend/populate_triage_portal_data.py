"""
Populate database with comprehensive data for Triage Portal testing.

This script creates:
- Organizations with bounty programs
- Researchers
- Triage specialist
- Vulnerability reports with various statuses
- Messages between triage and researchers
"""
import sys
from datetime import datetime, timedelta
from uuid import uuid4
from sqlalchemy.orm import Session

from src.core.database import SessionLocal
from src.domain.models.user import User
from src.domain.models.organization import Organization
from src.domain.models.program import BountyProgram
from src.domain.models.researcher import Researcher
from src.domain.models.report import VulnerabilityReport
from src.domain.models.staff_profiles import TriageSpecialist
from src.core.security import get_password_hash


def populate_data():
    """Populate database with test data."""
    db: Session = SessionLocal()
    
    try:
        print("=" * 60)
        print("POPULATING TRIAGE PORTAL DATA")
        print("=" * 60)
        
        # 1. Create Organizations
        print("\n1. Creating Organizations...")
        orgs = []
        org_names = [
            "Ethiopian Airlines",
            "Commercial Bank of Ethiopia",
            "Ethio Telecom",
            "Ethiopian Electric Power",
            "Awash Bank"
        ]
        
        for org_name in org_names:
            # Create user for organization
            org_user = User(
                id=uuid4(),
                email=f"{org_name.lower().replace(' ', '')}@example.com",
                password_hash=get_password_hash("Password123!"),
                role="ORGANIZATION",  # Uppercase to match database
                is_verified=True,
                is_active=True
            )
            db.add(org_user)
            db.flush()
            
            # Create organization profile
            org = Organization(
                id=uuid4(),
                user_id=org_user.id,
                company_name=org_name,
                website=f"https://{org_name.lower().replace(' ', '')}.com",
                industry="Technology",
                verification_status="verified"
            )
            db.add(org)
            orgs.append(org)
            print(f"   ✓ Created: {org_name}")
        
        db.commit()
        
        # 2. Create Bounty Programs
        print("\n2. Creating Bounty Programs...")
        programs = []
        for org in orgs:
            program = BountyProgram(
                id=uuid4(),
                organization_id=org.id,
                name=f"{org.company_name} Bug Bounty",
                description=f"Security testing program for {org.company_name}",
                type="bounty",
                status="public",
                visibility="public"
            )
            db.add(program)
            programs.append(program)
            print(f"   ✓ Created: {program.name}")
        
        db.commit()
        
        # 3. Create Researchers
        print("\n3. Creating Researchers...")
        researchers = []
        researcher_names = [
            ("Abraham", "Asimamaw"),
            ("Yohannes", "Tadesse"),
            ("Meron", "Bekele"),
            ("Daniel", "Haile"),
            ("Sara", "Tesfaye"),
            ("Michael", "Girma"),
            ("Ruth", "Alemayehu"),
            ("Samuel", "Kebede")
        ]
        
        for first, last in researcher_names:
            # Create user
            researcher_user = User(
                id=uuid4(),
                email=f"{first.lower()}.{last.lower()}@researcher.com",
                password_hash=get_password_hash("Password123!"),
                role="RESEARCHER",  # Uppercase to match database
                is_verified=True,
                is_active=True
            )
            db.add(researcher_user)
            db.flush()
            
            # Create researcher profile
            researcher = Researcher(
                id=uuid4(),
                user_id=researcher_user.id,
                first_name=first,
                last_name=last,
                bio=f"Security researcher specializing in web application security",
                reputation_score=750 + len(researchers) * 50
            )
            db.add(researcher)
            researchers.append(researcher)
            print(f"   ✓ Created: {first} {last}")
        
        db.commit()
        
        # 4. Create Triage Specialist
        print("\n4. Creating Triage Specialist...")
        triage_user = User(
            id=uuid4(),
            email="triage@bugbounty.com",
            password_hash=get_password_hash("Password123!"),
            role="triage_specialist",
            is_verified=True,
            is_active=True
        )
        db.add(triage_user)
        db.flush()
        
        triage_specialist = TriageSpecialist(
            id=uuid4(),
            user_id=triage_user.id,
            first_name="Triage",
            last_name="Specialist",
            specialization="Web Security"
        )
        db.add(triage_specialist)
        db.commit()
        print(f"   ✓ Created: Triage Specialist (triage@bugbounty.com)")
        
        # 5. Create Vulnerability Reports
        print("\n5. Creating Vulnerability Reports...")
        
        severities = ["critical", "high", "medium", "low"]
        statuses = ["new", "triaged", "valid", "invalid", "duplicate", "resolved"]
        vuln_types = [
            "SQL Injection",
            "Cross-Site Scripting (XSS)",
            "Authentication Bypass",
            "Insecure Direct Object Reference",
            "Server-Side Request Forgery",
            "Remote Code Execution",
            "Cross-Site Request Forgery",
            "Information Disclosure"
        ]
        
        report_count = 0
        now = datetime.utcnow()
        
        # Create reports with different statuses
        for i in range(80):
            researcher = researchers[i % len(researchers)]
            program = programs[i % len(programs)]
            severity = severities[i % len(severities)]
            status = statuses[i % len(statuses)]
            vuln_type = vuln_types[i % len(vuln_types)]
            
            # Calculate dates based on status
            submitted_at = now - timedelta(days=30 - (i % 30))
            triaged_at = None
            acknowledged_at = None
            resolved_at = None
            
            if status in ["triaged", "valid", "invalid", "duplicate", "resolved"]:
                triaged_at = submitted_at + timedelta(hours=2 + (i % 10))
            
            if status in ["valid", "resolved"]:
                acknowledged_at = triaged_at + timedelta(hours=1)
            
            if status == "resolved":
                resolved_at = acknowledged_at + timedelta(days=7 + (i % 14))
            
            report = VulnerabilityReport(
                id=uuid4(),
                report_number=f"VR-{2026}-{(i+1):04d}",
                program_id=program.id,
                researcher_id=researcher.id,
                title=f"{vuln_type} in {program.name.split()[0]} Application",
                description=f"Detailed description of {vuln_type.lower()} vulnerability found in the application. "
                           f"This vulnerability allows an attacker to compromise the system security.",
                vulnerability_type=vuln_type,
                severity=severity,
                suggested_severity=severity,
                assigned_severity=severity if status != "new" else None,
                status=status,
                cvss_score=7.5 if severity == "high" else 9.0 if severity == "critical" else 5.0,
                submitted_at=submitted_at,
                triaged_at=triaged_at,
                triaged_by=triage_specialist.id if triaged_at else None,
                acknowledged_at=acknowledged_at,
                resolved_at=resolved_at,
                bounty_amount=5000.0 if status == "valid" else None,
                is_duplicate=status == "duplicate"
            )
            db.add(report)
            report_count += 1
            
            if report_count % 20 == 0:
                print(f"   ✓ Created {report_count} reports...")
        
        db.commit()
        print(f"   ✓ Total reports created: {report_count}")
        
        # 6. Summary
        print("\n" + "=" * 60)
        print("DATA POPULATION COMPLETE")
        print("=" * 60)
        print(f"\n✓ Organizations: {len(orgs)}")
        print(f"✓ Bounty Programs: {len(programs)}")
        print(f"✓ Researchers: {len(researchers)}")
        print(f"✓ Triage Specialists: 1")
        print(f"✓ Vulnerability Reports: {report_count}")
        
        print("\n" + "=" * 60)
        print("LOGIN CREDENTIALS")
        print("=" * 60)
        print("\nTriage Specialist:")
        print("  Email: triage@bugbounty.com")
        print("  Password: Password123!")
        
        print("\nSample Researcher:")
        print("  Email: abraham.asimamaw@researcher.com")
        print("  Password: Password123!")
        
        print("\nSample Organization:")
        print("  Email: ethiopianairlines@example.com")
        print("  Password: Password123!")
        
        print("\n" + "=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    populate_data()
