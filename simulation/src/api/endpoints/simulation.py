"""
Simulation API Endpoints - FREQ-23, FREQ-24, FREQ-25, FREQ-26, FREQ-27, FREQ-28
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from uuid import UUID

from src.core.database import get_db
from src.services.simulation_service import SimulationService
from src.api.schemas.simulation import (
    SimulationCreate, SimulationResponse, SimulationUpdate,
    SimulationProgress, SimulationResult
)

router = APIRouter(prefix="/simulation", tags=["Simulation"])

@router.post("/start", response_model=SimulationResponse)
async def start_simulation(
    simulation_data: SimulationCreate,
    db: Session = Depends(get_db)
):
    """
    Start a new simulation session
    FREQ-23: Simulation Environment
    """
    try:
        service = SimulationService(db)
        simulation = service.start_simulation(
            user_id=simulation_data.user_id,
            level=simulation_data.level,
            target_id=simulation_data.target_id
        )
        return SimulationResponse.from_orm(simulation)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{simulation_id}", response_model=SimulationResponse)
async def get_simulation(
    simulation_id: UUID,
    db: Session = Depends(get_db)
):
    """Get simulation details"""
    try:
        service = SimulationService(db)
        simulation = service.get_simulation(str(simulation_id))
        if not simulation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Simulation not found"
            )
        return SimulationResponse.from_orm(simulation)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/user/{user_id}", response_model=List[SimulationResponse])
async def get_user_simulations(
    user_id: str,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get user's simulation history"""
    try:
        service = SimulationService(db)
        simulations = service.get_user_simulations(user_id, skip, limit)
        return [SimulationResponse.from_orm(sim) for sim in simulations]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/{simulation_id}/progress", response_model=SimulationProgress)
async def update_simulation_progress(
    simulation_id: UUID,
    progress_data: SimulationUpdate,
    db: Session = Depends(get_db)
):
    """
    Update simulation progress
    FREQ-24: Simulation Workflow Mirroring
    """
    try:
        service = SimulationService(db)
        progress = service.update_progress(
            str(simulation_id),
            progress_data.status,
            progress_data.current_step,
            progress_data.time_spent
        )
        return SimulationProgress.from_orm(progress)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/{simulation_id}/submit", response_model=SimulationResult)
async def submit_simulation_result(
    simulation_id: UUID,
    result_data: Dict,
    db: Session = Depends(get_db)
):
    """
    Submit simulation completion result
    FREQ-26: Simulation Reporting
    """
    try:
        service = SimulationService(db)
        result = service.submit_result(
            str(simulation_id),
            result_data.get("findings", []),
            result_data.get("time_taken", 0),
            result_data.get("hints_used", 0)
        )
        return SimulationResult.from_orm(result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{simulation_id}/feedback")
async def get_simulation_feedback(
    simulation_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get simulation feedback and scoring
    FREQ-28: Simulation Feedback
    """
    try:
        service = SimulationService(db)
        feedback = service.get_feedback(str(simulation_id))
        if not feedback:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Feedback not available"
            )
        return feedback
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/{simulation_id}")
async def delete_simulation(
    simulation_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete simulation session"""
    try:
        service = SimulationService(db)
        success = service.delete_simulation(str(simulation_id))
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Simulation not found"
            )
        return {"message": "Simulation deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/levels", response_model=List[Dict])
async def get_simulation_levels(db: Session = Depends(get_db)):
    """
    Get available simulation levels
    FREQ-25: Simulation Difficulty Levels
    """
    try:
        service = SimulationService(db)
        levels = service.get_available_levels()
        return levels
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/leaderboard")
async def get_simulation_leaderboard(
    level: Optional[str] = None,
    time_period: Optional[str] = "weekly",
    db: Session = Depends(get_db)
):
    """
    Get simulation leaderboard
    BR-13: Simulation scores visible only to user, not public
    """
    try:
        service = SimulationService(db)
        # Return empty leaderboard as per business rule
        return {
            "message": "Simulation scores are private and visible only to individual users",
            "leaderboard": [],
            "business_rule": "BR-13: Simulation scores are private"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
