"""
Researcher Repository - Data access layer for Researcher model
"""
import uuid

from sqlalchemy.orm import Session
from typing import Optional

from src.domain.models.researcher import Researcher


class ResearcherRepository:
    """Researcher repository for database operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, researcher_id: str) -> Optional[Researcher]:
        """Get researcher by ID"""
        if isinstance(researcher_id, str):
            researcher_id = uuid.UUID(researcher_id)
        return self.db.query(Researcher).filter(Researcher.id == researcher_id).first()

    def get(self, researcher_id: str) -> Optional[Researcher]:
        """Backward-compatible alias for fetching a researcher by ID."""
        return self.get_by_id(researcher_id)
    
    def get_by_user_id(self, user_id: str) -> Optional[Researcher]:
        """Get researcher by user ID"""
        return self.db.query(Researcher).filter(Researcher.user_id == user_id).first()
    
    def get_by_username(self, username: str) -> Optional[Researcher]:
        """Get researcher by username"""
        return self.db.query(Researcher).filter(Researcher.username == username).first()
    
    def get_by_ninja_email(self, ninja_email: str) -> Optional[Researcher]:
        """Get researcher by ninja email"""
        return self.db.query(Researcher).filter(Researcher.ninja_email == ninja_email).first()
    
    def create(self, researcher: Researcher) -> Researcher:
        """Create new researcher"""
        self.db.add(researcher)
        self.db.commit()
        self.db.refresh(researcher)
        return researcher
    
    def update(self, researcher: Researcher) -> Researcher:
        """Update existing researcher"""
        self.db.commit()
        self.db.refresh(researcher)
        return researcher
