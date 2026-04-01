"""
Scoring API Endpoints - FREQ-26, FREQ-28: Simulation Reporting & Feedback
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from uuid import UUID

from src.core.database import get_db
from src.services.scoring_service import ScoringService
from src.api.schemas.scoring import ScoreResponse, SimulationScoreResponse, FeedbackResponse

router = APIRouter(prefix="/scoring", tags=["Scoring"])

@router.get("/user/{user_id}")
async def get_user_scores(
    user_id: str,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get user's simulation scores"""
    try:
        service = ScoringService(db)
        scores = service.get_user_scores(user_id)
        return scores
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/simulation/{simulation_id}", response_model=SimulationScoreResponse)
async def get_simulation_score(
    simulation_id: UUID,
    db: Session = Depends(get_db)
):
    """Get detailed score breakdown for simulation"""
    try:
        service = ScoringService(db)
        score = service.get_simulation_score(str(simulation_id))
        if not score:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Score not found"
            )
        return service.get_simulation_score(str(simulation_id))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/calculate")
async def calculate_score(
    score_data: Dict,
    db: Session = Depends(get_db)
):
    """
    Calculate simulation score based on performance
    FREQ-26: Simulation Reporting
    """
    try:
        service = ScoringService(db)
        return service.calculate_score(
            findings=score_data.get("findings", []),
            time_taken=score_data.get("time_taken", 0),
            hints_used=score_data.get("hints_used", 0)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/feedback/{simulation_id}")
async def get_score_feedback(
    simulation_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get detailed feedback for simulation performance
    FREQ-28: Simulation Feedback
    """
    try:
        service = ScoringService(db)
        return service.get_score_feedback(str(simulation_id))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/analytics/{user_id}")
async def get_user_analytics(
    user_id: str,
    time_period: Optional[str] = "monthly",
    db: Session = Depends(get_db)
):
    """Get user's scoring analytics"""
    try:
        service = ScoringService(db)
        analytics = service.get_user_analytics(user_id, time_period)
        return analytics
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/leaderboard")
async def get_score_leaderboard(
    level: Optional[str] = None,
    time_period: Optional[str] = "weekly",
    db: Session = Depends(get_db)
):
    """
    Get simulation leaderboard
    BR-13: Simulation scores are private, not public
    """
    try:
        service = ScoringService(db)
        # Return empty leaderboard as per business rule
        return {
            "message": "Simulation scores are private and visible only to individual users",
            "leaderboard": [],
            "business_rule": "BR-13: Simulation scores do not contribute to public leaderboards"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
