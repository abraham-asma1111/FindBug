"""
Simulation Repository — simulated_environments, simulation_sessions
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from src.domain.repositories.base import BaseRepository
from src.domain.models.simulation import SimulatedEnvironment, SimulationSession


class SimulationRepository(BaseRepository[SimulatedEnvironment]):
    def __init__(self, db: Session):
        super().__init__(db, SimulatedEnvironment)

    # ─── Environments ─────────────────────────────────────────────────────

    def get_active_environments(self, difficulty: Optional[str] = None) -> List[SimulatedEnvironment]:
        query = self.db.query(SimulatedEnvironment).filter(
            SimulatedEnvironment.is_active == True
        )
        if difficulty:
            query = query.filter(SimulatedEnvironment.difficulty == difficulty)
        return query.order_by(SimulatedEnvironment.name).all()

    def get_environment_by_name(self, name: str) -> Optional[SimulatedEnvironment]:
        return (
            self.db.query(SimulatedEnvironment)
            .filter(SimulatedEnvironment.name == name)
            .first()
        )

    # ─── Sessions ─────────────────────────────────────────────────────────

    def get_sessions_by_researcher(
        self, researcher_id: str, skip: int = 0, limit: int = 20
    ) -> List[SimulationSession]:
        return (
            self.db.query(SimulationSession)
            .filter(SimulationSession.researcher_id == researcher_id)
            .order_by(SimulationSession.created_at.desc())
            .offset(skip).limit(limit).all()
        )

    def get_active_session(self, researcher_id: str) -> Optional[SimulationSession]:
        return (
            self.db.query(SimulationSession)
            .filter(
                SimulationSession.researcher_id == researcher_id,
                SimulationSession.status == "active",
            )
            .first()
        )

    def get_leaderboard(self, environment_id: str, limit: int = 10) -> List[SimulationSession]:
        return (
            self.db.query(SimulationSession)
            .filter(
                SimulationSession.environment_id == environment_id,
                SimulationSession.status == "completed",
            )
            .order_by(SimulationSession.score.desc(), SimulationSession.time_spent.asc())
            .limit(limit).all()
        )

    def complete_session(
        self, session_id: str, score: int, time_spent: int
    ) -> Optional[SimulationSession]:
        from datetime import datetime
        session = self.db.query(SimulationSession).filter(
            SimulationSession.id == session_id
        ).first()
        if not session:
            return None
        session.status = "completed"
        session.score = score
        session.time_spent = time_spent
        session.completed_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(session)
        return session
