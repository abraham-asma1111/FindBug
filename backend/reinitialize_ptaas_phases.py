"""
Script to reinitialize PTaaS engagement phases with checklist items
Run this to add checklist items to existing engagements
"""
import sys
from sqlalchemy.orm import Session
from src.core.database import SessionLocal
from src.domain.models.ptaas_dashboard import PTaaSTestingPhase, PTaaSChecklistItem
from src.services.ptaas_dashboard_service import PTaaSDashboardService

def reinitialize_engagement_phases(engagement_id: str):
    """Delete existing phases and reinitialize with checklists"""
    db: Session = SessionLocal()
    
    try:
        # Get engagement to check methodology
        from src.domain.models.ptaas import PTaaSEngagement
        engagement = db.query(PTaaSEngagement).filter(
            PTaaSEngagement.id == engagement_id
        ).first()
        
        if not engagement:
            print(f"❌ Engagement {engagement_id} not found")
            return
        
        print(f"📋 Engagement: {engagement.name}")
        print(f"🔧 Methodology: {engagement.testing_methodology}")
        
        # Delete existing phases and checklist items
        print("\n🗑️  Deleting existing phases and checklist items...")
        db.query(PTaaSChecklistItem).filter(
            PTaaSChecklistItem.engagement_id == engagement_id
        ).delete()
        
        db.query(PTaaSTestingPhase).filter(
            PTaaSTestingPhase.engagement_id == engagement_id
        ).delete()
        
        db.commit()
        print("✅ Deleted existing phases")
        
        # Reinitialize with checklist items
        print(f"\n🔄 Reinitializing {engagement.testing_methodology} phases with checklists...")
        dashboard_service = PTaaSDashboardService(db)
        phases = dashboard_service.initialize_engagement_phases(
            engagement_id, 
            engagement.testing_methodology
        )
        
        print(f"✅ Created {len(phases)} phases")
        
        # Count checklist items
        total_items = db.query(PTaaSChecklistItem).filter(
            PTaaSChecklistItem.engagement_id == engagement_id
        ).count()
        
        print(f"✅ Created {total_items} checklist items")
        print("\n✨ Done! Refresh your browser to see the changes.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python reinitialize_ptaas_phases.py <engagement_id>")
        print("\nExample:")
        print("  python reinitialize_ptaas_phases.py 2b59ff25-38bb-44c2-b1fc-7e76f8adfaaa")
        sys.exit(1)
    
    engagement_id = sys.argv[1]
    reinitialize_engagement_phases(engagement_id)
