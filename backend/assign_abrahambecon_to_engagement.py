"""
Assign abrahambecon researcher to a PTaaS engagement
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.domain.models.ptaas import PTaaSEngagement
from src.domain.models.user import User
from src.core.config import settings
from src.services.ptaas_service import PTaaSService

# Create database connection
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

def assign_abrahambecon():
    """Assign abrahambecon to an engagement"""
    
    # Find abrahambecon user
    researcher = db.query(User).filter(
        User.email.ilike('%abrahambecon%')
    ).first()
    
    if not researcher:
        # Try by email pattern
        researcher = db.query(User).filter(
            User.role == 'researcher'
        ).first()
        print(f"⚠️  User 'abrahambecon' not found. Using first researcher: {researcher.email if researcher else 'None'}")
    else:
        print(f"✅ Found researcher: {researcher.email} (ID: {researcher.id})")
    
    if not researcher:
        print("❌ No researcher found in database")
        print("\nAvailable researchers:")
        all_researchers = db.query(User).filter(User.role == 'researcher').all()
        for r in all_researchers:
            print(f"  - {r.email} (ID: {r.id})")
        return
    
    # Get an engagement
    engagement = db.query(PTaaSEngagement).first()
    if not engagement:
        print("❌ No engagement found in database")
        return
    
    print(f"✅ Found engagement: {engagement.name} (ID: {engagement.id})")
    print(f"   Status: {engagement.status}")
    print(f"   Current assigned researchers: {engagement.assigned_researchers}")
    
    # Check if already assigned
    if engagement.assigned_researchers and str(researcher.id) in engagement.assigned_researchers:
        print(f"\n⚠️  Researcher is already assigned to this engagement!")
        return
    
    # Assign researcher using service
    service = PTaaSService(db)
    
    # Get organization user for audit
    org_user = db.query(User).filter(User.role == 'organization').first()
    if not org_user:
        print("❌ No organization user found")
        return
    
    print(f"\n🔄 Assigning researcher to engagement...")
    updated_engagement = service.assign_researchers(
        engagement_id=engagement.id,
        researcher_ids=[researcher.id],
        assigned_by=org_user.id
    )
    
    if updated_engagement:
        print(f"\n✅ SUCCESS! Researcher assigned to engagement!")
        print(f"   Engagement: {updated_engagement.name}")
        print(f"   Assigned researchers: {updated_engagement.assigned_researchers}")
        print(f"   Team size: {updated_engagement.team_size}")
        print(f"\n📧 Researcher email: {researcher.email}")
        print(f"   Researcher ID: {researcher.id}")
        print(f"\n🔍 The researcher should now see this engagement at:")
        print(f"   GET /ptaas/researcher/engagements")
    else:
        print("\n❌ Failed to assign researcher")

if __name__ == "__main__":
    try:
        assign_abrahambecon()
        db.commit()
        print("\n✅ Database changes committed")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()
