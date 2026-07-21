"""
Verify abrahambecon can see their assigned engagements
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.domain.models.ptaas import PTaaSEngagement
from src.domain.models.user import User
from src.core.config import settings

# Create database connection
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

def verify_abrahambecon():
    """Verify abrahambecon can see engagements"""
    
    # Find abrahambecon user
    researcher = db.query(User).filter(
        User.email.ilike('%abrahambecon%')
    ).first()
    
    if not researcher:
        print("❌ User 'abrahambecon' not found")
        return
    
    print(f"✅ Found researcher: {researcher.email} (ID: {researcher.id})")
    print(f"   Role: {researcher.role}")
    
    researcher_id = str(researcher.id)
    
    # Simulate the API query (same logic as the fixed endpoint)
    print(f"\n🔍 Querying engagements for researcher...")
    query = db.query(PTaaSEngagement)
    all_engagements = query.order_by(PTaaSEngagement.created_at.desc()).all()
    
    # Filter for researcher in Python (same as fixed endpoint)
    engagements = [
        eng for eng in all_engagements
        if eng.assigned_researchers and researcher_id in eng.assigned_researchers
    ]
    
    print(f"\n📊 Results:")
    print(f"   Total engagements in database: {len(all_engagements)}")
    print(f"   Engagements assigned to {researcher.email}: {len(engagements)}")
    
    if len(engagements) > 0:
        print(f"\n✅ SUCCESS! Researcher can see {len(engagements)} engagement(s):")
        for eng in engagements:
            print(f"\n  📋 Engagement: {eng.name}")
            print(f"     ID: {eng.id}")
            print(f"     Status: {eng.status}")
            print(f"     Methodology: {eng.testing_methodology}")
            print(f"     Start Date: {eng.start_date}")
            print(f"     End Date: {eng.end_date}")
            print(f"     Assigned Researchers: {eng.assigned_researchers}")
            print(f"     Team Size: {eng.team_size}")
    else:
        print(f"\n❌ No engagements found for researcher")
        print(f"\n🔍 Checking all engagements:")
        for eng in all_engagements:
            print(f"\n  Engagement: {eng.name}")
            print(f"  Assigned: {eng.assigned_researchers}")
            print(f"  Contains researcher? {researcher_id in (eng.assigned_researchers or [])}")

if __name__ == "__main__":
    try:
        verify_abrahambecon()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()
