#!/usr/bin/env python3
"""
Check which organization owns the engagement with reports
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sqlalchemy.orm import Session
from src.core.database import SessionLocal
from src.domain.models.ai_red_teaming import AIRedTeamingEngagement
from src.domain.models.organization import Organization
from src.domain.models.user import User

def main():
    db: Session = SessionLocal()
    
    try:
        engagement_id = "37c63fe6-4b45-46ab-b72d-f7b16949b256"
        
        engagement = db.query(AIRedTeamingEngagement).filter(
            AIRedTeamingEngagement.id == engagement_id
        ).first()
        
        if not engagement:
            print("❌ Engagement not found!")
            return
        
        print(f"Engagement: {engagement.name}")
        print(f"ID: {engagement.id}")
        print(f"Organization ID: {engagement.organization_id}")
        
        # Find organization
        org = db.query(Organization).filter(
            Organization.id == engagement.organization_id
        ).first()
        
        if org:
            print(f"\nOrganization: {org.company_name}")
            print(f"Organization ID: {org.id}")
            
            # Find organization user
            user = db.query(User).filter(
                User.id == org.user_id
            ).first()
            
            if user:
                print(f"Organization User Email: {user.email}")
                print(f"\n✅ Login with: {user.email}")
            else:
                print("❌ Organization user not found!")
        else:
            print("❌ Organization not found!")
        
        # Also check org@example.com
        print("\n" + "="*60)
        print("Checking org@example.com user:")
        
        org_user = db.query(User).filter(User.email == "org@example.com").first()
        if org_user:
            print(f"User ID: {org_user.id}")
            
            org_profile = db.query(Organization).filter(
                Organization.user_id == org_user.id
            ).first()
            
            if org_profile:
                print(f"Organization: {org_profile.company_name}")
                print(f"Organization ID: {org_profile.id}")
                
                # Check engagements for this org
                engagements = db.query(AIRedTeamingEngagement).filter(
                    AIRedTeamingEngagement.organization_id == org_profile.id
                ).all()
                
                print(f"\nEngagements for org@example.com: {len(engagements)}")
                for eng in engagements:
                    print(f"  - {eng.name} (Status: {eng.status})")
            else:
                print("❌ No organization profile found for org@example.com")
        else:
            print("❌ org@example.com user not found!")
        
    finally:
        db.close()

if __name__ == "__main__":
    main()
