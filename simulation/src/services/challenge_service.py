"""
Challenge Service for Simulation Platform
"""

from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from uuid import UUID

from src.domain.models.simulation import SimulationChallenge, SimulationTarget
from src.core.exceptions import NotFoundException
from src.core.logging import get_logger

logger = get_logger(__name__)


class ChallengeService:
    """Handles challenge management"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_challenges(
        self,
        difficulty: Optional[str] = None,
        category: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> List[SimulationChallenge]:
        """Get available challenges with filters"""
        query = self.db.query(SimulationChallenge).filter(
            SimulationChallenge.is_active == True
        )
        
        if difficulty:
            query = query.filter(SimulationChallenge.difficulty == difficulty)
        
        if category:
            query = query.filter(SimulationChallenge.category == category)
        
        return query.offset(skip).limit(limit).all()
    
    def get_challenge(self, challenge_id: str) -> Optional[SimulationChallenge]:
        """Get challenge by ID"""
        return self.db.query(SimulationChallenge).filter(
            SimulationChallenge.id == challenge_id,
            SimulationChallenge.is_active == True
        ).first()
    
    def start_challenge(self, challenge_id: str, user_id: str) -> Dict:
        """Start a challenge attempt"""
        challenge = self.get_challenge(challenge_id)
        if not challenge:
            raise NotFoundException("Challenge not found")
        
        # Create attempt record (simplified)
        attempt = {
            "id": str(UUID()),
            "challenge_id": challenge_id,
            "user_id": user_id,
            "started_at": datetime.utcnow(),
            "status": "active"
        }
        
        return attempt
    
    def submit_solution(
        self,
        challenge_id: str,
        user_id: str,
        solution: str,
        time_taken: int
    ) -> Dict:
        """Submit challenge solution"""
        challenge = self.get_challenge(challenge_id)
        if not challenge:
            raise NotFoundException("Challenge not found")
        
        # Simplified solution validation
        attempt = {
            "id": str(UUID()),
            "challenge_id": challenge_id,
            "user_id": user_id,
            "solution": solution,
            "time_taken": time_taken,
            "submitted_at": datetime.utcnow(),
            "status": "submitted"
        }
        
        return attempt
    
    def get_hint(self, challenge_id: str, user_id: str, hint_number: int) -> Optional[str]:
        """Get challenge hint"""
        challenge = self.get_challenge(challenge_id)
        if not challenge or not challenge.hints:
            return None
        
        if hint_number < len(challenge.hints):
            return challenge.hints[hint_number]
        
        return None
    
    def get_categories(self) -> List[str]:
        """Get available challenge categories"""
        categories = self.db.query(SimulationChallenge.category).distinct().all()
        return [cat[0] for cat in categories]