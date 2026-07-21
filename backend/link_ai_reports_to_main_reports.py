#!/usr/bin/env python3
"""
Link AI Red Teaming vulnerability reports to the main reports table
so they appear in the organization's main reports page
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sqlalchemy.orm import Session
from src.core.database import SessionLocal
from src.domain.models.ai_red_teaming import AIVulnerabilityReport, AIRedTeamingEngagement
from src.domain.models.report import VulnerabilityReport
from src.domain.models.program import BountyProgram
from datetime import datetime

def main():
    db: Session = SessionLocal()
    
    try:
        print("=" * 60)
        print("LINKING AI RED TEAMING REPORTS TO MAIN REPORTS TABLE")
        print("=" * 60)
        
        # Get all AI vulnerability reports
        ai_reports = db.query(AIVulnerabilityReport).all()
        print(f"\nFound {len(ai_reports)} AI vulnerability report(s)")
        
        linked_count = 0
        
        for ai_report in ai_reports:
            # Check if already linked
            existing_report = db.query(VulnerabilityReport).filter(
                VulnerabilityReport.title == ai_report.title,
                VulnerabilityReport.researcher_id == ai_report.researcher_id
            ).first()
            
            if existing_report:
                print(f"\n  ⏭️  Report '{ai_report.title}' already exists in main reports table")
                continue
            
            # Get engagement details
            engagement = db.query(AIRedTeamingEngagement).filter(
                AIRedTeamingEngagement.id == ai_report.engagement_id
            ).first()
            
            if not engagement:
                print(f"\n  ❌ Engagement not found for report '{ai_report.title}'")
                continue
            
            # Find or create a program for this AI Red Teaming engagement
            # We'll use a special program name to identify AI Red Teaming reports
            program_name = f"AI Red Teaming: {engagement.name}"
            program = db.query(BountyProgram).filter(
                BountyProgram.name == program_name,
                BountyProgram.organization_id == engagement.organization_id
            ).first()
            
            if not program:
                # Create a program for this AI Red Teaming engagement
                program = BountyProgram(
                    name=program_name,
                    description=f"AI Red Teaming engagement for {engagement.target_ai_system}",
                    organization_id=engagement.organization_id,
                    type="bounty",
                    status="active",
                    created_at=engagement.created_at or datetime.utcnow()
                )
                db.add(program)
                db.flush()
                print(f"\n  ✅ Created program: {program_name}")
            
            # Create main report entry
            main_report = VulnerabilityReport(
                title=ai_report.title,
                description=f"{ai_report.impact}\n\nAttack Type: {ai_report.attack_type}\n\nInput Prompt: {ai_report.input_prompt}\n\nModel Response: {ai_report.model_response}",
                severity=ai_report.severity,
                status=ai_report.status.value if hasattr(ai_report.status, 'value') else str(ai_report.status),
                researcher_id=ai_report.researcher_id,
                program_id=program.id,
                submitted_at=ai_report.submitted_at or datetime.utcnow(),
                vulnerability_type=ai_report.attack_type.value if hasattr(ai_report.attack_type, 'value') else str(ai_report.attack_type),
                reproduction_steps=ai_report.reproduction_steps,
                mitigation_recommendation=ai_report.mitigation_recommendation
            )
            
            db.add(main_report)
            linked_count += 1
            
            print(f"\n  ✅ Linked AI report '{ai_report.title}' to main reports")
            print(f"     - Severity: {ai_report.severity}")
            print(f"     - Attack Type: {ai_report.attack_type}")
            print(f"     - Program: {program_name}")
        
        db.commit()
        
        print("\n" + "=" * 60)
        print(f"COMPLETE: Linked {linked_count} AI report(s) to main reports table")
        print("=" * 60)
        print("\nAI Red Teaming reports will now appear in:")
        print("  http://localhost:3000/organization/reports")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()
