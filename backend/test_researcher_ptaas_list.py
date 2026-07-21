"""
Test script to debug researcher PTaaS engagement listing
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import create_engine, cast, String, text
from sqlalchemy.orm import sessionmaker
from src.domain.models.ptaas import PTaaSEngagement
from src.domain.models.user import User
from src.core.config import settings

# Create database connection
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

def test_researcher_engagement_query():
    """Test different query methods to find researcher engagements"""
    
    # Get a researcher user
    researcher = db.query(User).filter(User.role == 'researcher').first()
    if not researcher:
        print("❌ No researcher found in database")
        return
    
    print(f"✅ Testing with researcher: {researcher.email} (ID: {researcher.id})")
    
    # Get all engagements
    all_engagements = db.query(PTaaSEngagement).all()
    print(f"\n📊 Total engagements in database: {len(all_engagements)}")
    
    for eng in all_engagements:
        print(f"\n  Engagement: {eng.name}")
        print(f"  ID: {eng.id}")
        print(f"  Status: {eng.status}")
        print(f"  Assigned Researchers: {eng.assigned_researchers}")
        print(f"  Type: {type(eng.assigned_researchers)}")
        
        if eng.assigned_researchers:
            print(f"  Contains researcher ID? {str(researcher.id) in eng.assigned_researchers}")
    
    # Method 1: Using cast and contains (current implementation)
    print("\n\n🔍 Method 1: Using cast(String).contains()")
    researcher_id = str(researcher.id)
    query1 = db.query(PTaaSEngagement).filter(
        cast(PTaaSEngagement.assigned_researchers, String).contains(researcher_id)
    )
    result1 = query1.all()
    print(f"Found {len(result1)} engagements")
    for eng in result1:
        print(f"  - {eng.name}")
    
    # Method 2: Using PostgreSQL JSON operators
    print("\n\n🔍 Method 2: Using PostgreSQL JSON operators")
    try:
        # Use PostgreSQL's @> operator for JSON containment
        query2 = db.query(PTaaSEngagement).filter(
            text(f"assigned_researchers @> ARRAY['{researcher_id}']::text[]")
        )
        result2 = query2.all()
        print(f"Found {len(result2)} engagements")
        for eng in result2:
            print(f"  - {eng.name}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Method 3: Using Python filtering (fallback)
    print("\n\n🔍 Method 3: Using Python filtering")
    all_engagements = db.query(PTaaSEngagement).all()
    result3 = [
        eng for eng in all_engagements 
        if eng.assigned_researchers and researcher_id in eng.assigned_researchers
    ]
    print(f"Found {len(result3)} engagements")
    for eng in result3:
        print(f"  - {eng.name}")
    
    # Method 4: Check if assigned_researchers is actually a list or string
    print("\n\n🔍 Method 4: Checking data types")
    for eng in all_engagements:
        if eng.assigned_researchers:
            print(f"\nEngagement: {eng.name}")
            print(f"  Type: {type(eng.assigned_researchers)}")
            print(f"  Value: {eng.assigned_researchers}")
            print(f"  Is list? {isinstance(eng.assigned_researchers, list)}")
            if isinstance(eng.assigned_researchers, list):
                print(f"  Length: {len(eng.assigned_researchers)}")
                print(f"  First item type: {type(eng.assigned_researchers[0]) if eng.assigned_researchers else 'N/A'}")

if __name__ == "__main__":
    try:
        test_researcher_engagement_query()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()
