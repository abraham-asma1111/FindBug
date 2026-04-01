"""
Targets API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from src.core.database import get_db
from src.domain.models.simulation import SimulationTarget
from src.api.schemas.target import TargetResponse

router = APIRouter(prefix="/targets", tags=["Targets"])


@router.get("/", response_model=List[TargetResponse])
async def get_targets(
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get available simulation targets"""
    try:
        query = db.query(SimulationTarget).filter(
            SimulationTarget.is_active == True
        )
        
        if category:
            query = query.filter(SimulationTarget.category == category)
        
        if difficulty:
            query = query.filter(SimulationTarget.difficulty == difficulty)
        
        targets = query.offset(skip).limit(limit).all()
        return [TargetResponse.from_orm(target) for target in targets]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{target_id}", response_model=TargetResponse)
async def get_target(
    target_id: UUID,
    db: Session = Depends(get_db)
):
    """Get target details"""
    try:
        target = db.query(SimulationTarget).filter(
            SimulationTarget.id == target_id,
            SimulationTarget.is_active == True
        ).first()
        
        if not target:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Target not found"
            )
        
        return TargetResponse.from_orm(target)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )