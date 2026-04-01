"""
Challenges API Endpoints - FREQ-23: Simulation Environment
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from uuid import UUID

from src.core.database import get_db
from src.services.challenge_service import ChallengeService
from src.api.schemas.challenge import ChallengeResponse, ChallengeAttempt

router = APIRouter(prefix="/challenges", tags=["Challenges"])

@router.get("/", response_model=List[ChallengeResponse])
async def get_available_challenges(
    difficulty: Optional[str] = None,
    category: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get available simulation challenges"""
    try:
        service = ChallengeService(db)
        challenges = service.get_challenges(difficulty, category, skip, limit)
        return [ChallengeResponse.from_orm(challenge) for challenge in challenges]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/{challenge_id}", response_model=ChallengeResponse)
async def get_challenge(
    challenge_id: UUID,
    db: Session = Depends(get_db)
):
    """Get challenge details"""
    try:
        service = ChallengeService(db)
        challenge = service.get_challenge(str(challenge_id))
        if not challenge:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Challenge not found"
            )
        return ChallengeResponse.from_orm(challenge)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/{challenge_id}/start")
async def start_challenge(
    challenge_id: UUID,
    user_id: str,
    db: Session = Depends(get_db)
):
    """Start a challenge attempt"""
    try:
        service = ChallengeService(db)
        attempt = service.start_challenge(str(challenge_id), user_id)
        return {"attempt_id": str(attempt.id), "message": "Challenge started"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/{challenge_id}/submit", response_model=ChallengeAttempt)
async def submit_challenge_solution(
    challenge_id: UUID,
    solution_data: Dict,
    db: Session = Depends(get_db)
):
    """Submit challenge solution"""
    try:
        service = ChallengeService(db)
        attempt = service.submit_solution(
            str(challenge_id),
            solution_data.get("user_id"),
            solution_data.get("solution"),
            solution_data.get("time_taken", 0)
        )
        return ChallengeAttempt.from_orm(attempt)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{challenge_id}/hint")
async def get_challenge_hint(
    challenge_id: UUID,
    user_id: str,
    hint_number: int,
    db: Session = Depends(get_db)
):
    """Get challenge hint"""
    try:
        service = ChallengeService(db)
        hint = service.get_hint(str(challenge_id), user_id, hint_number)
        if not hint:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hint not available"
            )
        return {"hint": hint, "penalty": True}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/categories")
async def get_challenge_categories(db: Session = Depends(get_db)):
    """Get available challenge categories"""
    try:
        service = ChallengeService(db)
        categories = service.get_categories()
        return categories
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
