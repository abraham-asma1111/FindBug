"""
Load Bugcrowd VRT data into database
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.services.vrt_service import VRTService

# Database URLs
PROD_DB = "postgresql://bugbounty_user:changeme123@localhost:5432/bug_bounty_production"
TEST_DB = "postgresql://bugbounty_user:changeme123@localhost:5432/test_bugbounty"

def load_vrt(db_url: str, db_name: str):
    """Load VRT data into specified database"""
    print(f"\n🔄 Loading VRT data into {db_name}...")
    
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        vrt_service = VRTService(db)
        result = vrt_service.load_vrt_from_json()
        
        print(f"✅ {db_name}: Loaded {result['categories']} categories and {result['entries']} entries")
        
        # Verify
        categories = vrt_service.get_all_categories()
        print(f"📊 {db_name}: Total categories in DB: {len(categories)}")
        
    except Exception as e:
        print(f"❌ {db_name}: Error loading VRT data: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("Loading Bugcrowd VRT Data")
    print("=" * 60)
    
    # Load into both databases
    load_vrt(PROD_DB, "Production DB")
    load_vrt(TEST_DB, "Test DB")
    
    print("\n✅ VRT data loading complete!")
