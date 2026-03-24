"""Reputation and Leaderboard API Endpoints - FREQ-11, BR-09."""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.role_access import can_update_reputation_admin
from src.api.v1.middlewares.auth import get_current_user
from src.domain.models.user import User
from src.services.reputation_service import ReputationService


router = APIRouter()


@router.get("/leaderboard", status_code=status.HTTP_200_OK)
def get_leaderboard(
    limit: int = Query(10, ge=1, le=100, description="Number of top researchers"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    db: Session = Depends(get_db)
):
    """
    Get public leaderboard - FREQ-11, BR-09.
    
    Shows top researchers by reputation score.
    Default: Top 10 researchers.
    
    Public endpoint - no authentication required.
    """
    service = ReputationService(db)
    
    leaderboard = service.get_leaderboard(limit=limit, offset=offset)
    
    return {
        "leaderboard": leaderboard,
        "total": len(leaderboard),
        "limit": limit,
        "offset": offset
    }


@router.get("/leaderboard/top-earners", status_code=status.HTTP_200_OK)
def get_top_earners(
    limit: int = Query(10, ge=1, le=100, description="Number of top earners"),
    db: Session = Depends(get_db)
):
    """
    Get top earners leaderboard.
    
    Alternative leaderboard based on total earnings.
    
    Public endpoint - no authentication required.
    """
    service = ReputationService(db)
    
    top_earners = service.get_top_earners(limit=limit)
    
    return {
        "top_earners": top_earners,
        "total": len(top_earners)
    }


@router.get("/researchers/{researcher_id}/profile", status_code=status.HTTP_200_OK)
def get_researcher_profile(
    researcher_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get researcher public profile - FREQ-11.
    
    Shows:
    - Reputation score and rank
    - Total earnings
    - Statistics (total reports, success rate, severity breakdown)
    - Social links
    
    Public endpoint - no authentication required.
    """
    service = ReputationService(db)
    
    try:
        profile = service.get_researcher_profile(researcher_id=researcher_id)
        return profile
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/researchers/{researcher_id}/rank", status_code=status.HTTP_200_OK)
def get_researcher_rank(
    researcher_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get researcher's current rank and percentile - FREQ-11.
    
    Shows:
    - Current rank
    - Total researchers
    - Percentile (top X%)
    - Reputation score
    
    Public endpoint - no authentication required.
    """
    service = ReputationService(db)
    
    try:
        rank_info = service.get_researcher_rank(researcher_id=researcher_id)
        return rank_info
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/my-reputation", status_code=status.HTTP_200_OK)
def get_my_reputation(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's reputation details - FREQ-11.
    
    Shows full profile including private statistics.
    
    Only researchers can access.
    """
    if current_user.role != "researcher":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only researchers have reputation scores"
        )
    
    service = ReputationService(db)
    
    try:
        # Get researcher profile
        profile = service.get_researcher_profile(researcher_id=current_user.researcher.id)
        
        # Get rank info
        rank_info = service.get_researcher_rank(researcher_id=current_user.researcher.id)
        
        return {
            "profile": profile,
            "rank_info": rank_info
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/researchers/{researcher_id}/update-reputation", status_code=status.HTTP_200_OK)
@router.get("/researchers/{researcher_id}/update-reputation", status_code=status.HTTP_200_OK)
def update_researcher_reputation(
    researcher_id: UUID,
    report_id: UUID = Query(..., description="Report ID to calculate reputation from"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Manually update researcher reputation - FREQ-11, BR-09.
    
    Called when report status changes to valid/invalid/duplicate.
    Normally triggered automatically by bounty approval/rejection.
    
    Only admins and triage specialists can manually trigger.
    """
    if not can_update_reputation_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins or triage specialists can update reputation"
        )
    
    service = ReputationService(db)
    
    try:
        # Get report
        from src.domain.repositories.report_repository import ReportRepository
        report_repo = ReportRepository(db)
        report = report_repo.get_by_id(report_id)
        
        if not report:
            raise ValueError("Report not found")
        
        # Update reputation
        researcher = service.update_reputation(
            researcher_id=researcher_id,
            report=report
        )
        
        return {
            "message": "Reputation updated successfully",
            "researcher_id": str(researcher.id),
            "reputation_score": float(researcher.reputation_score or 0),
            "rank": researcher.rank,
            "total_earnings": float(researcher.total_earnings or 0)
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
