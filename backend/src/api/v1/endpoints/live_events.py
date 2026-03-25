"""
Live Hacking Events API Endpoints
Implements FREQ-43, FREQ-44: Event Management and Real-time Dashboards
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from src.core.database import get_db
from src.api.v1.middlewares.auth import get_current_user
from src.domain.models.user import User
from src.services.live_event_service import LiveEventService
from src.domain.models.live_event import EventStatus, ParticipationStatus
from src.api.v1.schemas.live_event import (
    EventCreate,
    EventUpdate,
    EventResponse,
    InviteResearchersRequest,
    InvitationResponse,
    RespondToInvitationRequest,
    ParticipationResponse,
    EventMetricsResponse,
    LeaderboardResponse,
    LeaderboardEntry,
    EventDashboardResponse,
    ResearcherEventResponse,
    SubmitFindingRequest,
    EventStatusUpdate
)

router = APIRouter(prefix="/live-events", tags=["live-events"])


# ============================================
# ORGANIZATION ENDPOINTS
# ============================================

@router.post("", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(
    data: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create new live hacking event
    
    Requires organization admin role
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User must belong to an organization"
        )
    
    service = LiveEventService(db)
    
    event = service.create_event(
        organization_id=current_user.organization_id,
        name=data.name,
        description=data.description,
        start_time=data.start_time,
        end_time=data.end_time,
        max_participants=data.max_participants,
        prize_pool=data.prize_pool,
        scope_description=data.scope_description,
        target_assets=data.target_assets,
        reward_policy=data.reward_policy
    )
    
    return event


@router.get("", response_model=List[EventResponse])
def list_events(
    status_filter: Optional[str] = None,
    active_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List live hacking events
    
    Organizations see their own events
    Researchers see events they're invited to
    """
    service = LiveEventService(db)
    
    if current_user.organization_id:
        # Organization view - their events
        status_enum = EventStatus(status_filter) if status_filter else None
        events = service.list_events(
            organization_id=current_user.organization_id,
            status=status_enum,
            active_only=active_only
        )
    else:
        # Researcher view - invited events
        researcher_events = service.get_researcher_events(
            researcher_id=current_user.researcher.id if current_user.researcher else None
        )
        events = [re["event"] for re in researcher_events]
    
    return events


@router.get("/{event_id}", response_model=EventResponse)
def get_event(
    event_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get event by ID"""
    service = LiveEventService(db)
    event = service.get_event(event_id)
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Check access
    if current_user.organization_id:
        if event.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    return event


@router.patch("/{event_id}/status", response_model=EventResponse)
def update_event_status(
    event_id: UUID,
    data: EventStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update event status
    
    State transitions: draft → scheduled → active → closed → archived
    """
    service = LiveEventService(db)
    event = service.get_event(event_id)
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    if event.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    try:
        status_enum = EventStatus(data.status)
        event = service.update_event_status(event_id, status_enum)
        return event
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{event_id}/start", response_model=EventResponse)
def start_event(
    event_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Start event (transition to active)"""
    service = LiveEventService(db)
    event = service.get_event(event_id)
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    if event.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    try:
        event = service.start_event(event_id)
        return event
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{event_id}/close", response_model=EventResponse)
def close_event(
    event_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Close event (transition to closed)"""
    service = LiveEventService(db)
    event = service.get_event(event_id)
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    if event.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    try:
        event = service.close_event(event_id)
        return event
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{event_id}/invite", response_model=List[InvitationResponse])
def invite_researchers(
    event_id: UUID,
    data: InviteResearchersRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Invite researchers to event
    
    Requires organization admin role
    """
    service = LiveEventService(db)
    event = service.get_event(event_id)
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    if event.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    try:
        invitations = service.invite_researchers(
            event_id=event_id,
            researcher_ids=data.researcher_ids,
            expires_in_days=data.expires_in_days
        )
        return invitations
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ============================================
# ORGANIZATION DASHBOARD
# ============================================

@router.get("/{event_id}/dashboard", response_model=EventDashboardResponse)
def get_event_dashboard(
    event_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get real-time event dashboard for organization
    
    Includes:
    - Event details
    - Real-time metrics
    - Leaderboard
    - Recent submissions
    """
    service = LiveEventService(db)
    event = service.get_event(event_id)
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    if event.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Get metrics
    metrics = service.get_event_metrics(event_id)
    
    # Get leaderboard
    leaderboard_data = service.get_leaderboard(event_id, limit=10)
    leaderboard = [
        LeaderboardEntry(
            rank=p.rank or 0,
            researcher_id=p.researcher_id,
            researcher_name="Researcher",  # TODO: Join with researcher table
            score=p.score,
            submissions_count=p.submissions_count,
            valid_submissions_count=p.valid_submissions_count,
            prize_amount=p.prize_amount
        )
        for p in leaderboard_data
    ]
    
    return EventDashboardResponse(
        event=event,
        metrics=metrics,
        leaderboard=leaderboard,
        recent_submissions=[]  # TODO: Get recent submissions
    )


@router.get("/{event_id}/metrics", response_model=EventMetricsResponse)
def get_event_metrics(
    event_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get real-time event metrics"""
    service = LiveEventService(db)
    event = service.get_event(event_id)
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    if event.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    metrics = service.get_event_metrics(event_id)
    
    if not metrics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Metrics not found"
        )
    
    return metrics


@router.get("/{event_id}/leaderboard", response_model=LeaderboardResponse)
def get_leaderboard(
    event_id: UUID,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get event leaderboard"""
    service = LiveEventService(db)
    event = service.get_event(event_id)
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    leaderboard_data = service.get_leaderboard(event_id, limit=limit)
    
    entries = [
        LeaderboardEntry(
            rank=p.rank or 0,
            researcher_id=p.researcher_id,
            researcher_name="Researcher",  # TODO: Join with researcher table
            score=p.score,
            submissions_count=p.submissions_count,
            valid_submissions_count=p.valid_submissions_count,
            prize_amount=p.prize_amount
        )
        for p in leaderboard_data
    ]
    
    return LeaderboardResponse(
        event_id=event_id,
        event_name=event.name,
        entries=entries
    )


# ============================================
# RESEARCHER ENDPOINTS
# ============================================

@router.get("/researcher/my-events", response_model=List[ResearcherEventResponse])
def get_my_events(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get events for current researcher
    
    Includes invited, active, and completed events
    """
    if not current_user.researcher:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a researcher"
        )
    
    service = LiveEventService(db)
    researcher_events = service.get_researcher_events(
        researcher_id=current_user.researcher.id
    )
    
    results = []
    for re in researcher_events:
        event = re["event"]
        participation = re["participation"]
        
        # Calculate time remaining
        time_remaining = None
        if event.status == EventStatus.ACTIVE:
            delta = event.end_time - datetime.utcnow()
            time_remaining = int(delta.total_seconds() / 60)  # Minutes
        
        results.append(ResearcherEventResponse(
            event=event,
            participation=participation,
            my_rank=participation.rank,
            my_score=participation.score,
            time_remaining=time_remaining
        ))
    
    return results


@router.post("/invitations/{invitation_id}/respond", response_model=InvitationResponse)
def respond_to_invitation(
    invitation_id: UUID,
    data: RespondToInvitationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Respond to event invitation
    
    Researcher accepts or declines invitation
    """
    if not current_user.researcher:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a researcher"
        )
    
    service = LiveEventService(db)
    
    try:
        invitation = service.respond_to_invitation(
            invitation_id=invitation_id,
            researcher_id=current_user.researcher.id,
            accept=data.accept
        )
        return invitation
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{event_id}/submit", status_code=status.HTTP_200_OK)
def submit_finding(
    event_id: UUID,
    data: SubmitFindingRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Submit finding to live event
    
    Links vulnerability report to event
    """
    if not current_user.researcher:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a researcher"
        )
    
    service = LiveEventService(db)
    
    try:
        service.submit_finding(
            event_id=event_id,
            researcher_id=current_user.researcher.id,
            report_id=data.report_id
        )
        return {"message": "Finding submitted successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{event_id}/my-participation", response_model=ParticipationResponse)
def get_my_participation(
    event_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get researcher's participation in event"""
    if not current_user.researcher:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a researcher"
        )
    
    from src.domain.models.live_event import EventParticipation
    
    participation = db.query(EventParticipation).filter(
        EventParticipation.event_id == event_id,
        EventParticipation.researcher_id == current_user.researcher.id
    ).first()
    
    if not participation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Participation not found"
        )
    
    return participation
