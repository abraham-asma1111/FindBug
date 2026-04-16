#!/usr/bin/env python3
"""
Test publishing an AI Red Teaming engagement
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.services.ai_red_teaming_service import AIRedTeamingService
from src.domain.models.ai_red_teaming import EngagementStatus
from src.domain.models.user import User
import uuid

# Database connection
DATABASE_URL = "postgresql://bugbounty_user:changeme123@localhost:5432/bug_bounty_production"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def test_publish():
    db = SessionLocal()
    try:
        # Get organization user
        org_user = db.query(User).filter(User.email == "org@example.com").first()
        if not org_user:
            print("❌ Organization user not found")
            return
        
        print(f"✅ Found organization: {org_user.email}")
        print(f"   Organization ID: {org_user.organization.id}\n")
        
        # Create service
        service = AIRedTeamingService(db)
        
        # Create engagement
        print("Creating engagement...")
        engagement = service.create_engagement(
            organization_id=org_user.organization.id,
            name="Test Engagement",
            target_ai_system="Test System",
            model_type="llm",
            testing_environment="https://test.com",
            ethical_guidelines="Test guidelines",
            scope_description="Test scope",
            allowed_attack_types=["prompt_injection"]
        )
        
        print(f"✅ Created engagement: {engagement.id}")
        print(f"   Status: {engagement.status}\n")
        
        # Update status to active (this should trigger auto-broadcast)
        print("Publishing engagement (changing status to active)...")
        try:
            updated = service.update_engagement_status(
                engagement_id=engagement.id,
                status=EngagementStatus.ACTIVE
            )
            print(f"✅ Status updated to: {updated.status}")
            print(f"   Auto-broadcast should have been triggered\n")
            
            # Check researcher engagements
            print("Checking researcher engagements...")
            from src.domain.models.ai_red_teaming import ResearcherEngagement
            researcher_engagements = db.query(ResearcherEngagement).filter(
                ResearcherEngagement.engagement_id == engagement.id
            ).all()
            
            print(f"✅ Found {len(researcher_engagements)} researcher engagement(s)")
            for re in researcher_engagements[:3]:
                print(f"   - Researcher ID: {re.researcher_id}, Status: {re.status}")
            
        except Exception as e:
            print(f"❌ Error updating status: {e}")
            import traceback
            traceback.print_exc()
        
    finally:
        db.close()

if __name__ == "__main__":
    test_publish()
