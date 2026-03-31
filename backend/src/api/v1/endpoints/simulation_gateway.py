"""
Simulation Platform Gateway API - FREQ-23 to FREQ-28
Acts as gateway to isolated simulation platform
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from src.core.database import get_db
from src.api.v1.middlewares.auth import get_current_user
from src.domain.models.user import User
from src.services.simulation_api_client import get_simulation_client, SimulationAPIError

router = APIRouter(prefix="/simulation", tags=["Simulation Platform Gateway"])


@router.get("/challenges")
async def get_challenges(
    difficulty: Optional[str] = Query(None, description="beginner, intermediate, advanced, expert"),
    category: Optional[str] = Query(None, description="web, mobile, api, network"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user)
):
    """
    Get available simulation challenges - FREQ-23
    Gateway to simulation platform challenge list
    """
    try:
        client = await get_simulation_client()
        challenges = await client.get_challenges(
            difficulty=difficulty,
            category=category, 
            skip=skip,
            limit=limit
        )
        
        return {
            "challenges": challenges,
            "user_id": str(current_user.id),
            "total": len(challenges)
        }
        
    except SimulationAPIError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch challenges"
        )


@router.get("/challenges/{challenge_id}")
async def get_challenge_details(
    challenge_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get challenge details with resources and community solutions - FREQ-23
    """
    try:
        client = await get_simulation_client()
        challenge = await client.get_challenge_details(challenge_id)
        
        return {
            "challenge": challenge,
            "user_id": str(current_user.id),
            "access_granted": True
        }
        
    except SimulationAPIError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch challenge details"
        )


@router.post("/challenges/{challenge_id}/start")
async def start_challenge(
    challenge_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Start challenge container - FREQ-24: Isolated Simulation Environment
    """
    try:
        client = await get_simulation_client()
        
        # Start challenge in simulation platform
        result = await client.start_challenge(challenge_id, str(current_user.id))
        
        return {
            "message": "Challenge started successfully",
            "challenge_id": challenge_id,
            "user_id": str(current_user.id),
            "container_info": result,
            "status": "active"
        }
        
    except SimulationAPIError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start challenge"
        )


@router.post("/challenges/{challenge_id}/stop")
async def stop_challenge(
    challenge_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Stop challenge container - FREQ-24
    """
    try:
        client = await get_simulation_client()
        result = await client.stop_challenge(challenge_id, str(current_user.id))
        
        return {
            "message": "Challenge stopped successfully",
            "challenge_id": challenge_id,
            "user_id": str(current_user.id),
            "status": "stopped"
        }
        
    except SimulationAPIError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to stop challenge"
        )


@router.post("/challenges/{challenge_id}/submit")
async def submit_simulation_report(
    challenge_id: str,
    report_data: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """
    Submit simulation report for manual triage - FREQ-26
    """
    try:
        client = await get_simulation_client()
        
        # Submit report to simulation platform for manual triage
        result = await client.submit_simulation_report(
            challenge_id=challenge_id,
            user_id=str(current_user.id),
            report_data=report_data
        )
        
        return {
            "message": "Report submitted for manual triage",
            "report_id": result.get("report_id"),
            "challenge_id": challenge_id,
            "user_id": str(current_user.id),
            "status": "submitted",
            "triage_status": "pending_manual_review"
        }
        
    except SimulationAPIError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit report"
        )


@router.get("/reports/{report_id}")
async def get_report_details(
    report_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get simulation report details and triage results
    """
    try:
        client = await get_simulation_client()
        # This would need to be implemented in simulation platform
        # For now, return placeholder
        return {
            "report_id": report_id,
            "user_id": str(current_user.id),
            "status": "pending_manual_review",
            "message": "Report is being manually reviewed by staff"
        }
        
    except SimulationAPIError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch report details"
        )


@router.get("/my-reports")
async def get_my_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user)
):
    """
    Get user's simulation reports
    """
    try:
        # This would call simulation platform API
        return {
            "reports": [],
            "user_id": str(current_user.id),
            "total": 0,
            "message": "Simulation reports are managed in the isolated platform"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch reports"
        )


@router.get("/my-progress")
async def get_my_progress(
    current_user: User = Depends(get_current_user)
):
    """
    Get user's simulation progress - FREQ-27
    """
    try:
        client = await get_simulation_client()
        progress = await client.get_user_scores(str(current_user.id))
        
        return {
            "user_id": str(current_user.id),
            "progress": progress,
            "platform": "simulation"
        }
        
    except SimulationAPIError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch progress"
        )


@router.get("/leaderboard")
async def get_leaderboard(
    period: str = Query("weekly", description="weekly, monthly, all-time"),
    limit: int = Query(100, ge=1, le=500)
):
    """
    Get simulation leaderboard - FREQ-26
    Note: Returns empty as per business rule BR-13 (simulation scores are private)
    """
    try:
        return {
            "leaderboard": [],
            "message": "Simulation scores are private and visible only to individual users",
            "business_rule": "BR-13: Simulation scores are private",
            "period": period,
            "limit": limit
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch leaderboard"
        )


@router.get("/my-stats")
async def get_my_stats(
    current_user: User = Depends(get_current_user)
):
    """
    Get user's simulation statistics - FREQ-28
    """
    try:
        client = await get_simulation_client()
        stats = await client.get_user_scores(str(current_user.id))
        
        return {
            "user_id": str(current_user.id),
            "stats": stats,
            "privacy_note": "Your simulation scores are private and only visible to you"
        }
        
    except SimulationAPIError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch statistics"
        )


@router.get("/health")
async def simulation_health():
    """
    Check simulation platform health
    """
    try:
        client = await get_simulation_client()
        is_healthy = await client.health_check()
        
        return {
            "simulation_platform": "healthy" if is_healthy else "unhealthy",
            "status": "connected" if is_healthy else "disconnected"
        }
        
    except Exception as e:
        return {
            "simulation_platform": "unhealthy",
            "status": "disconnected",
            "error": str(e)
        }