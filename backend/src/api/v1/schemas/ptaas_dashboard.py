"""
PTaaS Dashboard Schemas - FREQ-34
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# Testing Phase Schemas
class PTaaSTestingPhaseCreate(BaseModel):
    engagement_id: int
    phase_name: str = Field(..., max_length=100)
    phase_order: int
    description: Optional[str] = None
    assigned_to: Optional[int] = None
    estimated_completion: Optional[datetime] = None


class PTaaSTestingPhaseUpdate(BaseModel):
    phase_name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    status: Optional[str] = None
    progress_percentage: Optional[int] = Field(None, ge=0, le=100)
    assigned_to: Optional[int] = None
    estimated_completion: Optional[datetime] = None


class PTaaSTestingPhaseResponse(BaseModel):
    id: int
    engagement_id: int
    phase_name: str
    phase_order: int
    description: Optional[str]
    status: str
    progress_percentage: int
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    estimated_completion: Optional[datetime]
    assigned_to: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Checklist Item Schemas
class PTaaSChecklistItemCreate(BaseModel):
    phase_id: int
    engagement_id: int
    item_name: str = Field(..., max_length=255)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    is_required: bool = True


class PTaaSChecklistItemComplete(BaseModel):
    notes: Optional[str] = None
    evidence_url: Optional[str] = Field(None, max_length=500)


class PTaaSChecklistItemResponse(BaseModel):
    id: int
    phase_id: int
    engagement_id: int
    item_name: str
    description: Optional[str]
    category: Optional[str]
    is_completed: bool
    is_required: bool
    completed_by: Optional[int]
    completed_at: Optional[datetime]
    notes: Optional[str]
    evidence_url: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Collaboration Update Schemas
class PTaaSCollaborationUpdateCreate(BaseModel):
    engagement_id: int
    update_type: str = Field(..., max_length=50)
    title: Optional[str] = Field(None, max_length=255)
    content: str
    mentioned_users: Optional[List[int]] = None
    priority: str = Field(default="NORMAL", max_length=20)
    related_finding_id: Optional[int] = None
    related_phase_id: Optional[int] = None
    attachments: Optional[List[str]] = None


class PTaaSCollaborationUpdateResponse(BaseModel):
    id: int
    engagement_id: int
    update_type: str
    title: Optional[str]
    content: str
    created_by: int
    created_at: datetime
    mentioned_users: Optional[List[int]]
    is_pinned: bool
    priority: str
    related_finding_id: Optional[int]
    related_phase_id: Optional[int]
    attachments: Optional[List[str]]

    class Config:
        from_attributes = True


# Milestone Schemas
class PTaaSMilestoneCreate(BaseModel):
    engagement_id: int
    milestone_name: str = Field(..., max_length=255)
    description: Optional[str] = None
    target_date: datetime
    deliverables: Optional[List[str]] = None


class PTaaSMilestoneUpdate(BaseModel):
    milestone_name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    target_date: Optional[datetime] = None
    status: Optional[str] = None
    deliverables: Optional[List[str]] = None


class PTaaSMilestoneResponse(BaseModel):
    id: int
    engagement_id: int
    milestone_name: str
    description: Optional[str]
    target_date: datetime
    completed_date: Optional[datetime]
    status: str
    deliverables: Optional[List[str]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Dashboard Response
class PTaaSDashboardResponse(BaseModel):
    engagement: dict
    phases: List[dict]
    findings: dict
    collaboration: List[dict]
    team: dict
