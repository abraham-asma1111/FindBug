"""
Code Review API Schemas
Implements FREQ-41: Expert Code Review System
"""
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from enum import Enum


class ReviewTypeEnum(str, Enum):
    """Code review types"""
    SECURITY = "security"
    PERFORMANCE = "performance"
    BEST_PRACTICES = "best_practices"
    ARCHITECTURE = "architecture"
    FULL_REVIEW = "full_review"


class ReviewStatusEnum(str, Enum):
    """Code review engagement status"""
    PENDING = "pending"
    MATCHING = "matching"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    UNDER_REVIEW = "under_review"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class FindingSeverityEnum(str, Enum):
    """Code review finding severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class FindingStatusEnum(str, Enum):
    """Code review finding status"""
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    FIXED = "fixed"
    WONT_FIX = "wont_fix"
    FALSE_POSITIVE = "false_positive"


class IssueTypeEnum(str, Enum):
    """Types of code issues"""
    DEAD_CODE = "dead_code"
    INSECURE_DEPENDENCY = "insecure_dependency"
    LOGIC_FLAW = "logic_flaw"
    SECURITY_VULNERABILITY = "security_vulnerability"
    PERFORMANCE_ISSUE = "performance_issue"
    CODE_SMELL = "code_smell"
    MEMORY_LEAK = "memory_leak"
    RACE_CONDITION = "race_condition"
    OTHER = "other"


# Request Schemas
class CreateEngagementRequest(BaseModel):
    """Request to create a code review engagement"""
    title: str = Field(..., min_length=1, max_length=200)
    repository_url: str = Field(..., max_length=500)
    review_type: ReviewTypeEnum


class AssignReviewerRequest(BaseModel):
    """Request to assign a reviewer"""
    reviewer_id: UUID


class AddFindingRequest(BaseModel):
    """Request to add a finding"""
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    severity: FindingSeverityEnum
    issue_type: IssueTypeEnum
    file_path: Optional[str] = Field(None, max_length=500)
    line_number: Optional[int] = Field(None, ge=1)


class UpdateFindingStatusRequest(BaseModel):
    """Request to update finding status"""
    status: FindingStatusEnum


# Response Schemas
class CodeReviewFindingResponse(BaseModel):
    """Code review finding response"""
    id: UUID
    engagement_id: UUID
    title: str
    description: str
    severity: FindingSeverityEnum
    issue_type: IssueTypeEnum
    file_path: Optional[str]
    line_number: Optional[int]
    status: FindingStatusEnum
    created_at: datetime

    class Config:
        from_attributes = True


class CodeReviewEngagementResponse(BaseModel):
    """Code review engagement response"""
    id: UUID
    organization_id: UUID
    reviewer_id: Optional[UUID]
    title: str
    repository_url: str
    review_type: ReviewTypeEnum
    status: ReviewStatusEnum
    findings_count: int
    report_submitted_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class EngagementStatsResponse(BaseModel):
    """Engagement statistics response"""
    total_findings: int
    by_severity: dict
    by_status: dict
    by_issue_type: dict


class EngagementListResponse(BaseModel):
    """List of engagements response"""
    engagements: List[CodeReviewEngagementResponse]
    total: int


class FindingListResponse(BaseModel):
    """List of findings response"""
    findings: List[CodeReviewFindingResponse]
    total: int
