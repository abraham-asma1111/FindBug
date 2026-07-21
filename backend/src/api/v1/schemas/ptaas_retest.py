"""
PTaaS Retest Schemas - FREQ-37
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from enum import Enum


class RetestResult(str, Enum):
    """Enum for retest results"""
    FIXED = "FIXED"
    NOT_FIXED = "NOT_FIXED"
    PARTIALLY_FIXED = "PARTIALLY_FIXED"
    NEW_ISSUE = "NEW_ISSUE"


# Retest Policy Schemas
class PTaaSRetestPolicyCreate(BaseModel):
    retest_period_months: int = Field(default=12, ge=1, le=36)
    max_free_retests_per_finding: int = Field(default=3, ge=1, le=10)
    eligible_severities: Optional[List[str]] = Field(default=['Critical', 'High', 'Medium', 'Low'])
    requires_fix_evidence: bool = True
    requires_approval: bool = False
    target_turnaround_days: int = Field(default=5, ge=1, le=30)
    allow_partial_fixes: bool = True
    allow_new_findings_during_retest: bool = True
    notify_on_request: bool = True
    notify_on_completion: bool = True


class PTaaSRetestPolicyResponse(BaseModel):
    id: UUID
    engagement_id: UUID
    retest_period_months: int
    max_free_retests_per_finding: int
    eligible_severities: Optional[List[str]]
    requires_fix_evidence: bool
    requires_approval: bool
    target_turnaround_days: int
    allow_partial_fixes: bool
    allow_new_findings_during_retest: bool
    notify_on_request: bool
    notify_on_completion: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Retest Request Schemas
class PTaaSRetestRequestCreate(BaseModel):
    fix_description: str = Field(..., min_length=20)
    fix_implemented_at: Optional[datetime] = None
    fix_evidence: Optional[List[str]] = Field(None, description="URLs to fix evidence")


class PTaaSRetestRequestResponse(BaseModel):
    id: UUID
    finding_id: UUID
    engagement_id: UUID
    requested_by: UUID
    requested_at: datetime
    status: str
    fix_description: str
    fix_implemented_at: Optional[datetime]
    fix_evidence: Optional[List[str]]
    assigned_to: Optional[UUID]
    assigned_at: Optional[datetime]
    retest_started_at: Optional[datetime]
    retest_completed_at: Optional[datetime]
    retest_result: Optional[str]
    retest_notes: Optional[str]
    retest_evidence: Optional[List[str]]
    is_eligible: bool
    eligibility_expires_at: datetime
    eligibility_reason: Optional[str]
    is_free_retest: bool
    retest_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PTaaSRetestAssignment(BaseModel):
    assigned_to: UUID = Field(..., description="User ID to assign retest to")


class PTaaSRetestCompletion(BaseModel):
    retest_result: RetestResult = Field(..., description="Result of the retest")
    retest_notes: str = Field(..., min_length=20, description="Detailed notes about the retest")
    retest_evidence: Optional[List[str]] = Field(default=None, description="URLs to retest evidence")


class PTaaSRetestEligibilityResponse(BaseModel):
    is_eligible: bool
    reason: str
    retests_remaining: Optional[int] = None
    expires_at: Optional[datetime] = None


class PTaaSRetestStatisticsResponse(BaseModel):
    total_requests: int
    pending: int
    approved: int
    in_progress: int
    completed: int
    rejected: int
    free_retests: int
    paid_retests: int
    results: Dict[str, int]
