#!/usr/bin/env python3
"""
Debug script to check AI Red Teaming reports in database
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sqlalchemy.orm import Session
from src.core.database import SessionLocal
from src.domain.models.ai_red_teaming import AIRedTeamingEngagement, AIVulnerabilityReport
from src.domain.models.user import User
from src.domain.models.researcher import Researcher

def main():
    db: Session = SessionLocal()
    
    try:
        print("=" * 60)
        print("AI RED TEAMING REPORTS DEBUG")
        print("=" * 60)
        
        # Check engagements
        print("\n1. Checking AI Red Teaming Engagements:")
        engagements = db.query(AIRedTeamingEngagement).all()
        print(f"   Found {len(engagements)} engagement(s)")
        
        for eng in engagements:
            print(f"\n   Engagement: {eng.name}")
            print(f"   ID: {eng.id}")
            print(f"   Status: {eng.status}")
            print(f"   Organization ID: {eng.organization_id}")
            
            # Check reports for this engagement
            reports = db.query(AIVulnerabilityReport).filter(
                AIVulnerabilityReport.engagement_id == eng.id
            ).all()
            
            print(f"   Reports: {len(reports)}")
            
            if reports:
                for report in reports:
                    print(f"\n      Report: {report.title}")
                    print(f"      ID: {report.id}")
                    print(f"      Researcher ID: {report.researcher_id}")
                    print(f"      Attack Type: {report.attack_type}")
                    print(f"      Severity: {report.severity}")
                    print(f"      Status: {report.status}")
                    print(f"      Submitted At: {report.submitted_at}")
        
        # Check all reports
        print("\n\n2. Checking All AI Vulnerability Reports:")
        all_reports = db.query(AIVulnerabilityReport).all()
        print(f"   Total reports in database: {len(all_reports)}")
        
        for report in all_reports:
            print(f"\n   Report: {report.title}")
            print(f"   ID: {report.id}")
            print(f"   Engagement ID: {report.engagement_id}")
            print(f"   Researcher ID: {report.researcher_id}")
            print(f"   Attack Type: {report.attack_type}")
            print(f"   Severity: {report.severity}")
            
            # Check if engagement exists
            engagement = db.query(AIRedTeamingEngagement).filter(
                AIRedTeamingEngagement.id == report.engagement_id
            ).first()
            
            if engagement:
                print(f"   ✅ Engagement exists: {engagement.name}")
            else:
                print(f"   ❌ Engagement NOT FOUND!")
            
            # Check if researcher exists
            researcher = db.query(Researcher).filter(
                Researcher.id == report.researcher_id
            ).first()
            
            if researcher:
                user = db.query(User).filter(User.id == researcher.user_id).first()
                print(f"   ✅ Researcher exists: {user.email if user else 'Unknown'}")
            else:
                print(f"   ❌ Researcher NOT FOUND!")
        
        print("\n" + "=" * 60)
        print("DEBUG COMPLETE")
        print("=" * 60)
        
    finally:
        db.close()

if __name__ == "__main__":
    main()
