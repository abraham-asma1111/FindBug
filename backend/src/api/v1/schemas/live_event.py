"""
Live Hacking Events API Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from uuid import UUID
from decimal import Decimal


class EventCreate(BaseModel):
    """Schema for creating live event"""
    name: str = Field(..., min_length=3, max_length=200)
    description: str
    start_time: datetime
    end_time: datetime
    max_participants: Optional[int] = None
    prize_pool: Optional[Decimal] = None
    scope_description: Optional[str] = None
    target_assets: Optional[str] = None
    reward_policy: Optional[str] = None


class EventUpdate(BaseModel):
    """Schema for updating live event"""
    name: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    max_participants: Optional[int] = None
    prize_pool: Optional[Decimal] = None
    scope_description: Optional[str] = None
    target_assets: Optional[str] = None
    reward_policy: Optional[str] = None


class EventResponse(BaseModel):
    """Schema for event response"""
    id: UUID
    organization_id: UUID
    name: str
    description: Optional[str]
    status: str
    start_time: datetime
    end_time: datetime
    max_participants: Optional[int]
    prize_pool: Optional[Decimal]
    scope_description: Optional[str]
    target_assets: Optional[str]
    reward_policy: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class InviteResearchersRequest(BaseModel):
    """Schema for inviting researchers"""
    researcher_ids: List[UUID] = Field(..., min_items=1)
    expires_in_days: int = Field(default=7, ge=1, le=30)


class InvitationResponse(BaseModel):
    """Schema for invitation response"""
    id: UUID
    event_id: UUID
    researcher_id: UUID
    status: str
    invited_at: datetime
    responded_at: Optional[datetime]
    expires_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class RespondToInvitationRequest(BaseModel):
    """Schema for responding to invitation"""
    accept: bool


class ParticipationResponse(BaseModel):
    """Schema for participation response"""
    id: UUID
    event_id: UUID
    researcher_id: UUID
    status: str
    score: int
    rank: Optional[int]
    submissions_count: int
    valid_submissions_count: int
    prize_amount: Optional[Decimal]
    joined_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class EventMetricsResponse(BaseModel):
    """Schema for event metrics response"""
    id: UUID
    event_id: UUID
    
    # Participation metrics
    total_invited: int
    total_accepted: int
    total_active: int
    
    # Submission metrics
    total_submissions: int
    valid_submissions: int
    invalid_submissions: int
    duplicate_submissions: int
    
    # Severity breakdown
    critical_bugs: int
    high_bugs: int
    medium_bugs: int
    low_bugs: int
    info_bugs: int
    
    # Reward metrics
    total_rewards_paid: Decimal
    average_reward: Decimal
    
    # Performance metrics
    participation_rate: Decimal
    average_time_to_first_bug: Optional[int]
    
    last_updated: datetime
    
    class Config:
        from_attributes = True


class LeaderboardEntry(BaseModel):
    """Schema for leaderboard entry"""
    rank: int
    researcher_id: UUID
    researcher_name: str
    score: int
    submissions_count: int
    valid_submissions_count: int
    prize_amount: Optional[Decimal]


class LeaderboardResponse(BaseModel):
    """Schema for leaderboard response"""
    event_id: UUID
    event_name: str
    entries: List[LeaderboardEntry]


class EventDashboardResponse(BaseModel):
    """Schema for organization event dashboard"""
    event: EventResponse
    metrics: EventMetricsResponse
    leaderboard: List[LeaderboardEntry]
    recent_submissions: List[Dict]


class ResearcherEventResponse(BaseModel):
    """Schema for researcher event view"""
    event: EventResponse
    participation: ParticipationResponse
    my_rank: Optional[int]
    my_score: int
    time_remaining: Optional[int]  # Minutes


class SubmitFindingRequest(BaseModel):
    """Schema for submitting finding to event"""
    report_id: UUID


class EventStatusUpdate(BaseModel):
    """Schema for updating event status"""
    status: str = Field(..., pattern="^(draft|scheduled|active|closed|archived)$")
