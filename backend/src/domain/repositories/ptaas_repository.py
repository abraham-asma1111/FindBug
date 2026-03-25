"""
PTaaS Repository
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime
from src.domain.models.ptaas import (
    PTaaSEngagement, PTaaSFinding, PTaaSDeliverable, PTaaSProgressUpdate
)


class PTaaSRepository:
    """Repository for PTaaS operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # Engagement CRUD
    def create_engagement(self, engagement_data: dict) -> PTaaSEngagement:
        engagement = PTaaSEngagement(**engagement_data)
        self.db.add(engagement)
        self.db.commit()
        self.db.refresh(engagement)
        return engagement
    
    def get_engagement_by_id(self, engagement_id: int) -> Optional[PTaaSEngagement]:
        return self.db.query(PTaaSEngagement).filter(PTaaSEngagement.id == engagement_id).first()
    
    def get_engagements_by_organization(self, organization_id: int) -> List[PTaaSEngagement]:
        return self.db.query(PTaaSEngagement).filter(
            PTaaSEngagement.organization_id == organization_id
        ).all()
    
    def get_active_engagements(self) -> List[PTaaSEngagement]:
        return self.db.query(PTaaSEngagement).filter(
            PTaaSEngagement.status.in_(["ACTIVE", "IN_PROGRESS"])
        ).all()
    
    def update_engagement(self, engagement_id: int, update_data: dict) -> Optional[PTaaSEngagement]:
        engagement = self.get_engagement_by_id(engagement_id)
        if engagement:
            for key, value in update_data.items():
                setattr(engagement, key, value)
            engagement.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(engagement)
        return engagement
    
    def delete_engagement(self, engagement_id: int) -> bool:
        engagement = self.get_engagement_by_id(engagement_id)
        if engagement:
            self.db.delete(engagement)
            self.db.commit()
            return True
        return False
    
    # Finding CRUD
    def create_finding(self, finding_data: dict) -> PTaaSFinding:
        finding = PTaaSFinding(**finding_data)
        self.db.add(finding)
        self.db.commit()
        self.db.refresh(finding)
        return finding
    
    def get_findings_by_engagement(self, engagement_id: int) -> List[PTaaSFinding]:
        return self.db.query(PTaaSFinding).filter(
            PTaaSFinding.engagement_id == engagement_id
        ).all()
    
    def get_finding_by_id(self, finding_id: int) -> Optional[PTaaSFinding]:
        return self.db.query(PTaaSFinding).filter(PTaaSFinding.id == finding_id).first()
    
    def update_finding(self, finding_id: int, update_data: dict) -> Optional[PTaaSFinding]:
        finding = self.get_finding_by_id(finding_id)
        if finding:
            for key, value in update_data.items():
                setattr(finding, key, value)
            self.db.commit()
            self.db.refresh(finding)
        return finding
    
    # Deliverable CRUD
    def create_deliverable(self, deliverable_data: dict) -> PTaaSDeliverable:
        deliverable = PTaaSDeliverable(**deliverable_data)
        self.db.add(deliverable)
        self.db.commit()
        self.db.refresh(deliverable)
        return deliverable
    
    def get_deliverables_by_engagement(self, engagement_id: int) -> List[PTaaSDeliverable]:
        return self.db.query(PTaaSDeliverable).filter(
            PTaaSDeliverable.engagement_id == engagement_id
        ).all()
    
    def approve_deliverable(self, deliverable_id: int, approved_by: int) -> Optional[PTaaSDeliverable]:
        deliverable = self.db.query(PTaaSDeliverable).filter(
            PTaaSDeliverable.id == deliverable_id
        ).first()
        if deliverable:
            deliverable.approved = True
            deliverable.approved_by = approved_by
            deliverable.approved_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(deliverable)
        return deliverable
    
    # Progress Update CRUD
    def create_progress_update(self, update_data: dict) -> PTaaSProgressUpdate:
        progress_update = PTaaSProgressUpdate(**update_data)
        self.db.add(progress_update)
        self.db.commit()
        self.db.refresh(progress_update)
        return progress_update
    
    def get_progress_updates_by_engagement(self, engagement_id: int) -> List[PTaaSProgressUpdate]:
        return self.db.query(PTaaSProgressUpdate).filter(
            PTaaSProgressUpdate.engagement_id == engagement_id
        ).order_by(PTaaSProgressUpdate.created_at.desc()).all()
