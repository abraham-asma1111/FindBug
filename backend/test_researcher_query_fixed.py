"""
Test the fixed researcher engagement query
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

def test_fixed_query():
    """Test the fixed query method"""
    
    # Get a researcher user
    researcher = db.query(User).filter(User.role == 'researcher').first()
    if not researcher:
        print("❌ No researcher found in database")
        return
    
    print(f"✅ Testing with researcher: {researcher.email} (ID: {researcher.id})")
    
    researcher_id = str(researcher.id)
    
    # Method: Get all and filter in Python (the fix we applied)
    print("\n🔍 Using Python filtering (FIXED METHOD)")
    query = db.query(PTaaSEngagement)
    all_engagements = query.order_by(PTaaSEngagement.created_at.desc()).all()
    
    # Filter for researcher in Python
    engagements = [
        eng for eng in all_engagements
        if eng.assigned_researchers and researcher_id in eng.assigned_researchers
    ]
    
    print(f"✅ Found {len(engagements)} engagement(s) for researcher")
    
    for eng in engagements:
        print(f"\n  📋 Engagement: {eng.name}")
        print(f"     ID: {eng.id}")
        print(f"     Status: {eng.status}")
        print(f"     Methodology: {eng.testing_methodology}")
        print(f"     Assigned Researchers: {eng.assigned_researchers}")
        print(f"     Team Size: {eng.team_size}")
        print(f"     Start Date: {eng.start_date}")
        print(f"     End Date: {eng.end_date}")
    
    if len(engagements) == 0:
        print("\n⚠️  No engagements found. The researcher is not assigned to any engagements.")
        print("   Run 'python assign_researcher_to_engagement.py' to assign them.")

if __name__ == "__main__":
    try:
        test_fixed_query()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()
