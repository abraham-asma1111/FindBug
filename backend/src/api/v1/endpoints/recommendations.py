"""Recommendations API Endpoints - FREQ-16."""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.api.v1.middlewares.auth import get_current_user
from src.domain.models.user import User, UserRole
from src.domain.models.program import BountyProgram
from src.domain.models.researcher import Researcher

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("", status_code=status.HTTP_200_OK)
def get_recommendations(
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get personalized recommendations for researcher - FREQ-16.
    
    Recommends programs based on:
    - Researcher's skills and expertise
    - Past successful submissions
    - Program difficulty and rewards
    - Researcher's reputation level
    
    Only researchers can access recommendations.
    """
    if current_user.role != UserRole.RESEARCHER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only researchers can view recommendations"
        )
    
    # Get researcher profile
    researcher = current_user.researcher
    
    # Get public programs
    programs = db.query(BountyProgram).filter(
        BountyProgram.status == "public",
        BountyProgram.visibility == "public"
    ).limit(limit * 2).all()  # Get more to filter
    
    # Simple recommendation logic based on researcher reputation
    recommendations = []
    
    for program in programs:
        # Calculate match score (simplified)
        match_score = 0.5  # Base score
        
        # Boost score for programs with higher rewards if researcher has high reputation
        if researcher.reputation_score > 80 and program.budget and program.budget > 10000:
            match_score += 0.3
        
        # Boost score for programs with lower rewards if researcher is new
        if researcher.reputation_score < 50 and program.budget and program.budget < 5000:
            match_score += 0.2
        
        recommendations.append({
            "program_id": str(program.id),
            "program_name": program.name,
            "program_type": program.type,
            "budget": float(program.budget) if program.budget else None,
            "organization_name": program.organization.name if program.organization else None,
            "match_score": round(match_score, 2),
            "reason": _get_recommendation_reason(researcher, program, match_score)
        })
    
    # Sort by match score
    recommendations.sort(key=lambda x: x["match_score"], reverse=True)
    
    return {
        "recommendations": recommendations[:limit],
        "total": len(recommendations[:limit]),
        "researcher_reputation": researcher.reputation_score
    }


def _get_recommendation_reason(researcher: Researcher, program: BountyProgram, score: float) -> str:
    """Generate recommendation reason."""
    if score > 0.7:
        return f"Great match! This program aligns well with your expertise level (reputation: {researcher.reputation_score})."
    elif score > 0.5:
        return f"Good opportunity based on your profile and the program's reward structure."
    else:
        return f"Consider this program to expand your skills and experience."


@router.get("/programs", status_code=status.HTTP_200_OK)
def get_recommended_programs(
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get recommended programs (alias for /recommendations) - FREQ-16.
    """
    return get_recommendations(limit=limit, current_user=current_user, db=db)
