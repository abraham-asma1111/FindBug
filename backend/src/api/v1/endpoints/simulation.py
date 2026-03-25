"""
Simulation Platform API Endpoints
Implements FREQ-23 to FREQ-28
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from src.core.database import get_db
from src.api.v1.middlewares.auth import get_current_user
from src.domain.models.user import User
from src.services.simulation_service import SimulationService
from src.services.container_service import ContainerOrchestrationService
from src.api.v1.schemas.simulation import (
    ChallengeListResponse,
    ChallengeDetailsResponse,
    StartChallengeRequest,
    StartChallengeResponse,
    StopChallengeResponse,
    SubmitReportRequest,
    SubmitReportResponse,
    ReportDetailsResponse,
    SubmitSolutionRequest,
    SolutionResponse,
    ProgressResponse,
    LeaderboardResponse
)

router = APIRouter(prefix="/simulation", tags=["Simulation Platform"])

simulation_service = SimulationService()
container_service = ContainerOrchestrationService()


# FREQ-23: Provide simulation environment with vulnerable applications
# FREQ-25: Support beginner, intermediate, and advanced levels
@router.get("/challenges", response_model=List[ChallengeListResponse])
@router.post("/challenges", response_model=List[ChallengeListResponse])
async def get_challenges(
    difficulty: Optional[str] = Query(None, description="beginner, intermediate, advanced, expert"),
    severity: Optional[str] = Query(None, description="low, medium, high, critical"),
    category: Optional[str] = Query(None, description="xss, sqli, idor, csrf, etc."),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get list of simulation challenges with filters
    
    FREQ-23: Provides simulated vulnerable applications
    FREQ-25: Supports filtering by difficulty levels
    FREQ-27: Isolated from real bug bounty data
    """
    challenges = await simulation_service.get_challenges(
        db=db,
        difficulty=difficulty,
        severity=severity,
        category=category,
        skip=skip,
        limit=limit
    )
    return challenges


# FREQ-23: Get challenge details with resources
@router.get("/challenges/{challenge_id}", response_model=ChallengeDetailsResponse)
@router.post("/challenges/{challenge_id}", response_model=ChallengeDetailsResponse)
async def get_challenge_details(
    challenge_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed challenge information including:
    - Challenge description
    - Tutorial videos
    - Documentation
    - Hints
    - Community solutions
    
    FREQ-23: Provides challenge details
    FREQ-28: Provides learning hints
    """
    try:
        result = await simulation_service.get_challenge_details(
            db=db,
            challenge_id=challenge_id,
            user_id=str(current_user.id)
        )
        return result['challenge']
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


# FREQ-23: Start challenge instance (spin up Docker container)
# FREQ-24: Mirror real bug bounty workflows
@router.post("/challenges/{challenge_id}/start", response_model=StartChallengeResponse)
async def start_challenge(
    challenge_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Start a challenge instance
    - Spins up Docker container with vulnerable app
    - Returns unique URL for user to access
    - Instance expires after 2 hours
    
    FREQ-23: Provides simulated vulnerable application
    FREQ-24: Mirrors real bug bounty workflow
    FREQ-27: Isolated environment
    """
    try:
        # Check if user already has active instance
        existing = await container_service.get_user_active_instance(
            db=db,
            user_id=str(current_user.id),
            challenge_id=challenge_id
        )
        
        if existing:
            return {
                'instance_id': existing.instance_id,
                'url': existing.unique_url,
                'port': existing.port,
                'expires_at': existing.expires_at.isoformat(),
                'status': existing.status,
                'message': 'Using existing active instance'
            }
        
        # Get challenge details
        from src.domain.models.simulation import SimulationChallenge
        challenge = db.query(SimulationChallenge).filter(
            SimulationChallenge.id == challenge_id
        ).first()
        
        if not challenge:
            raise HTTPException(status_code=404, detail="Challenge not found")
        
        # Start new instance
        instance = await container_service.start_challenge_instance(
            db=db,
            user_id=str(current_user.id),
            challenge_id=challenge_id,
            challenge=challenge
        )
        
        return {
            **instance,
            'message': 'Challenge instance started successfully! Access the vulnerable app at the provided URL.'
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start challenge: {str(e)}")


# FREQ-23: Stop challenge instance
@router.post("/instances/{instance_id}/stop", response_model=StopChallengeResponse)
async def stop_challenge(
    instance_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Stop a running challenge instance
    - Stops Docker container
    - Frees up resources
    
    FREQ-27: Proper isolation and cleanup
    """
    try:
        result = await container_service.stop_challenge_instance(
            db=db,
            instance_id=instance_id
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# FREQ-24: Mirror real bug bounty workflow - Submit report
# FREQ-26: Submit simulated reports without affecting real programs
# FREQ-28: Provide automated feedback
@router.post("/reports", response_model=SubmitReportResponse)
async def submit_simulation_report(
    report_data: SubmitReportRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit a simulation vulnerability report
    - Mirrors real bug bounty report submission
    - Provides automated validation and feedback
    - Awards points for correct reports
    - Does NOT affect real programs
    
    FREQ-24: Mirrors real bug bounty workflow
    FREQ-26: Simulated reports only
    FREQ-27: Isolated from real data
    FREQ-28: Automated feedback
    """
    try:
        result = await simulation_service.submit_report(
            db=db,
            user_id=str(current_user.id),
            challenge_id=report_data.challenge_id,
            report_data=report_data.dict()
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# FREQ-28: Get report with feedback
@router.get("/reports/{report_id}", response_model=ReportDetailsResponse)
@router.post("/reports/{report_id}", response_model=ReportDetailsResponse)
async def get_report_details(
    report_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get simulation report details with feedback
    
    FREQ-28: Provides automated feedback and learning hints
    """
    from src.domain.models.simulation import SimulationReport
    
    report = db.query(SimulationReport).filter(
        SimulationReport.id == report_id,
        SimulationReport.user_id == current_user.id
    ).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return report


# FREQ-24: Get user's simulation reports
@router.get("/my-reports", response_model=List[ReportDetailsResponse])
@router.post("/my-reports", response_model=List[ReportDetailsResponse])
async def get_my_reports(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all simulation reports submitted by current user
    
    FREQ-24: Mirrors real bug bounty workflow
    FREQ-27: Isolated simulation data
    """
    from src.domain.models.simulation import SimulationReport
    
    reports = db.query(SimulationReport).filter(
        SimulationReport.user_id == current_user.id
    ).order_by(SimulationReport.submitted_at.desc()).all()
    
    return reports


# FREQ-28: Request hint for challenge
@router.post("/challenges/{challenge_id}/hint")
async def request_hint(
    challenge_id: str,
    hint_number: int = Query(..., ge=1, le=3),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Request a hint for a challenge
    - Hint 1: Free
    - Hint 2: Costs points
    - Hint 3: Costs more points
    
    FREQ-28: Provides learning hints
    """
    from src.domain.models.simulation import SimulationChallenge, SimulationProgress
    
    challenge = db.query(SimulationChallenge).filter(
        SimulationChallenge.id == challenge_id
    ).first()
    
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    
    # Get user progress
    progress = db.query(SimulationProgress).filter(
        SimulationProgress.user_id == current_user.id,
        SimulationProgress.challenge_id == challenge_id
    ).first()
    
    if not progress:
        progress = SimulationProgress(
            user_id=current_user.id,
            challenge_id=challenge_id,
            status="in_progress"
        )
        db.add(progress)
    
    # Check if hint already used
    if progress.hints_used >= hint_number:
        hint_key = f"hint{hint_number}"
        return {
            'hint': challenge.hints.get(hint_key),
            'cost': 0,
            'message': 'Hint already unlocked'
        }
    
    # Get hint cost
    hint_key = f"hint{hint_number}"
    cost = challenge.hint_costs.get(hint_key, 0)
    
    # Update progress
    progress.hints_used = hint_number
    db.commit()
    
    return {
        'hint': challenge.hints.get(hint_key),
        'cost': cost,
        'message': f'Hint {hint_number} unlocked'
    }


# Community Solutions
@router.get("/challenges/{challenge_id}/solutions", response_model=List[SolutionResponse])
@router.post("/challenges/{challenge_id}/solutions", response_model=List[SolutionResponse])
async def get_community_solutions(
    challenge_id: str,
    db: Session = Depends(get_db)
):
    """
    Get community solutions for a challenge
    Only shows approved solutions
    
    FREQ-28: Provides learning resources
    """
    from src.domain.models.simulation import SimulationSolution
    
    solutions = db.query(SimulationSolution).filter(
        SimulationSolution.challenge_id == challenge_id,
        SimulationSolution.is_approved == True
    ).order_by(SimulationSolution.likes_count.desc()).limit(20).all()
    
    return solutions


@router.post("/solutions", response_model=SolutionResponse)
async def submit_solution(
    solution_data: SubmitSolutionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit a community solution (writeup)
    Requires moderation approval
    
    FREQ-28: Community learning resources
    """
    try:
        solution = await simulation_service.submit_solution(
            db=db,
            user_id=str(current_user.id),
            challenge_id=solution_data.challenge_id,
            solution_data=solution_data.dict()
        )
        return solution
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Progress and Stats
@router.get("/progress", response_model=List[ProgressResponse])
@router.post("/progress", response_model=List[ProgressResponse])
async def get_my_progress(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's progress across all challenges
    
    FREQ-24: Track simulation progress
    """
    from src.domain.models.simulation import SimulationProgress
    
    progress = db.query(SimulationProgress).filter(
        SimulationProgress.user_id == current_user.id
    ).all()
    
    return progress


# FREQ-24: Leaderboard (gamification)
@router.get("/leaderboard", response_model=LeaderboardResponse)
@router.post("/leaderboard", response_model=LeaderboardResponse)
async def get_leaderboard(
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """
    Get simulation leaderboard
    Shows top performers in simulation mode
    
    FREQ-24: Mirrors real bug bounty gamification
    FREQ-27: Separate from real platform leaderboard
    """
    entries = await simulation_service.get_leaderboard(db=db, limit=limit)
    
    return {
        'entries': entries,
        'total_entries': len(entries)
    }


# User Statistics
@router.get("/stats")
@router.post("/stats")
async def get_my_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's simulation statistics
    
    FREQ-24: Track user performance
    """
    from src.domain.models.simulation import (
        SimulationProgress,
        SimulationReport,
        SimulationLeaderboard
    )
    
    # Get progress stats
    total_challenges = db.query(SimulationProgress).filter(
        SimulationProgress.user_id == current_user.id
    ).count()
    
    completed_challenges = db.query(SimulationProgress).filter(
        SimulationProgress.user_id == current_user.id,
        SimulationProgress.status == "completed"
    ).count()
    
    # Get report stats
    total_reports = db.query(SimulationReport).filter(
        SimulationReport.user_id == current_user.id
    ).count()
    
    correct_reports = db.query(SimulationReport).filter(
        SimulationReport.user_id == current_user.id,
        SimulationReport.is_correct == True
    ).count()
    
    # Get leaderboard position
    leaderboard = db.query(SimulationLeaderboard).filter(
        SimulationLeaderboard.user_id == current_user.id
    ).first()
    
    return {
        'total_challenges_attempted': total_challenges,
        'challenges_completed': completed_challenges,
        'total_reports_submitted': total_reports,
        'correct_reports': correct_reports,
        'success_rate': (correct_reports / total_reports * 100) if total_reports > 0 else 0,
        'total_points': leaderboard.total_points if leaderboard else 0,
        'rank': leaderboard.rank if leaderboard else None
    }
