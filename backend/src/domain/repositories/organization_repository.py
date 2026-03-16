"""
Organization Repository - Data access layer for Organization model
"""
from sqlalchemy.orm import Session
from typing import Optional

from src.domain.models.organization import Organization


class OrganizationRepository:
    """Organization repository for database operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, organization_id: str) -> Optional[Organization]:
        """Get organization by ID"""
        return self.db.query(Organization).filter(Organization.id == organization_id).first()
    
    def get_by_user_id(self, user_id: str) -> Optional[Organization]:
        """Get organization by user ID"""
        return self.db.query(Organization).filter(Organization.user_id == user_id).first()
    
    def create(self, organization: Organization) -> Organization:
        """Create new organization"""
        self.db.add(organization)
        self.db.commit()
        self.db.refresh(organization)
        return organization
    
    def update(self, organization: Organization) -> Organization:
        """Update existing organization"""
        self.db.commit()
        self.db.refresh(organization)
        return organization
