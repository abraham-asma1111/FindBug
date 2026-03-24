"""
AI Red Teaming Repository — ai_red_teaming_engagements & ai_vulnerability_reports
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from src.domain.repositories.base import BaseRepository
from src.domain.models.ai_red_teaming import AIRedTeamingEngagement


class AIRedTeamRepository(BaseRepository[AIRedTeamingEngagement]):
    def __init__(self, db: Session):
        super().__init__(db, AIRedTeamingEngagement)

    def get_by_organization(self, org_id: str, skip: int = 0, limit: int = 20) -> List[AIRedTeamingEngagement]:
        return (
            self.db.query(AIRedTeamingEngagement)
            .filter(AIRedTeamingEngagement.organization_id == org_id)
            .order_by(AIRedTeamingEngagement.created_at.desc())
            .offset(skip).limit(limit).all()
        )

    def get_by_expert(self, expert_id: str, skip: int = 0, limit: int = 20) -> List[AIRedTeamingEngagement]:
        return (
            self.db.query(AIRedTeamingEngagement)
            .filter(AIRedTeamingEngagement.expert_id == expert_id)
            .offset(skip).limit(limit).all()
        )

    def get_by_status(self, status: str) -> List[AIRedTeamingEngagement]:
        return (
            self.db.query(AIRedTeamingEngagement)
            .filter(AIRedTeamingEngagement.status == status)
            .all()
        )

    def update_status(self, engagement_id: str, status: str) -> Optional[AIRedTeamingEngagement]:
        engagement = self.get_by_id(engagement_id)
        if not engagement:
            return None
        engagement.status = status
        self.db.commit()
        self.db.refresh(engagement)
        return engagement

    def increment_findings(self, engagement_id: str) -> Optional[AIRedTeamingEngagement]:
        engagement = self.get_by_id(engagement_id)
        if not engagement:
            return None
        engagement.findings_count = (engagement.findings_count or 0) + 1
        self.db.commit()
        self.db.refresh(engagement)
        return engagement
