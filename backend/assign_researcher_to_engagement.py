#!/usr/bin/env python3
"""
Assign a researcher to an existing PTaaS engagement for testing
"""
import sys
import os
from uuid import UUID

sys.path.insert(0, os.path.dirname(__file__))

from src.core.database import SessionLocal
from src.domain.models.ptaas import PTaaSEngagement
from src.domain.models.user import User

def assign_researcher():
    db = SessionLocal()
    try:
        # Get first engagement
        engagement = db.query(PTaaSEngagement).first()
        
        if not engagement:
            print("❌ No PTaaS engagements found in database")
            print("Create an engagement first from the organization portal")
            return
        
        # Get researcher user
        researcher = db.query(User).filter(
            User.email == "researcher@test.com",
            User.role == "researcher"
        ).first()
        
        if not researcher:
            print("❌ Researcher user not found")
            print("Run: python create_researcher_user.py")
            return
        
        # Assign researcher to engagement
        researcher_id = str(researcher.id)
        
        if engagement.assigned_researchers is None:
            engagement.assigned_researchers = []
        
        if researcher_id not in engagement.assigned_researchers:
            engagement.assigned_researchers.append(researcher_id)
            db.commit()
            print(f"✅ Assigned researcher to engagement: {engagement.name}")
            print(f"   Engagement ID: {engagement.id}")
            print(f"   Researcher ID: {researcher_id}")
            print(f"   Researcher Email: {researcher.email}")
        else:
            print(f"ℹ️  Researcher already assigned to engagement: {engagement.name}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    assign_researcher()
