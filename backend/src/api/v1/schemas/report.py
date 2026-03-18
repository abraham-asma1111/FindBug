"""Vulnerability Report API schemas."""
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, validator


# Report submission schemas
class ReportCreate(BaseModel):
    """Schema for creating a vulnerability report - FREQ-06."""
    program_id: UUID
    title: str = Field(..., min_length=10, max_length=500)
    description: str = Field(..., min_length=50)
    steps_to_reproduce: str = Field(..., min_length=20)
    impact_assessment: str = Field(..., min_length=20)
    suggested_severity: str = Field(..., pattern="^(critical|high|medium|low)$")
    affected_asset: Optional[str] = Field(None, max_length=500)
    vulnerability_type: Optional[str] = Field(None, max_length=100)
    
    @validator('title')
    def title_must_be_descriptive(cls, v):
        if len(v.strip()) < 10:
            raise ValueError('Title must be at least 10 characters')
        return v.strip()


class ReportUpdate(BaseModel):
    """Schema for updating a report (by researcher)."""
    title: Optional[str] = Field(None, min_length=10, max_length=500)
    description: Optional[str] = Field(None, min_length=50)
    steps_to_reproduce: Optional[str] = Field(None, min_length=20)
    impact_assessment: Optional[str] = Field(None, min_length=20)
    suggested_severity: Optional[str] = Field(None, pattern="^(critical|high|medium|low)$")
    affected_asset: Optional[str] = Field(None, max_length=500)
    vulnerability_type: Optional[str] = Field(None, max_length=100)


# Triage schemas - FREQ-07, FREQ-08
class TriageUpdate(BaseModel):
    """Schema for triage specialist to update report."""
    status: Optional[str] = Field(None, pattern="^(new|triaged|valid|invalid|duplicate|resolved|closed)$")
    assigned_severity: Optional[str] = Field(None, pattern="^(critical|high|medium|low)$")
    cvss_score: Optional[Decimal] = Field(None, ge=0.0, le=10.0)
    vrt_category: Optional[str] = Field(None, max_length=100)
    triage_notes: Optional[str] = None
    is_duplicate: Optional[bool] = None
    duplicate_of: Optional[UUID] = None


class BountyApproval(BaseModel):
    """Schema for bounty approval - FREQ-10."""
    bounty_amount: Decimal = Field(..., gt=0)
    bounty_status: str = Field(..., pattern="^(approved|rejected)$")


# Comment schemas - FREQ-09
class CommentCreate(BaseModel):
    """Schema for creating a comment."""
    comment_text: str = Field(..., min_length=1, max_length=5000)
    comment_type: str = Field(default="comment", pattern="^(comment|status_change|severity_change|internal_note)$")
    is_internal: bool = Field(default=False)


class CommentResponse(BaseModel):
    """Schema for comment response."""
    id: UUID
    report_id: UUID
    comment_text: str
    comment_type: str
    is_internal: bool
    author_id: UUID
    author_role: str
    created_at: datetime
    updated_at: datetime
    edited: bool
    
    class Config:
        from_attributes = True


# Attachment schemas
class AttachmentResponse(BaseModel):
    """Schema for attachment response."""
    id: UUID
    report_id: UUID
    filename: str
    original_filename: str
    file_type: str
    file_size: int
    is_safe: bool
    uploaded_by: UUID
    uploaded_at: datetime
    
    class Config:
        from_attributes = True


# Report response schemas
class ReportResponse(BaseModel):
    """Schema for vulnerability report response."""
    id: UUID
    report_number: str
    program_id: UUID
    researcher_id: UUID
    
    # Content
    title: str
    description: str
    steps_to_reproduce: str
    impact_assessment: str
    suggested_severity: str
    affected_asset: Optional[str]
    vulnerability_type: Optional[str]
    
    # Status
    status: str
    assigned_severity: Optional[str]
    cvss_score: Optional[Decimal]
    vrt_category: Optional[str]
    
    # Triage
    triaged_by: Optional[UUID]
    triaged_at: Optional[datetime]
    triage_notes: Optional[str]
    
    # Duplicate
    is_duplicate: bool
    duplicate_of: Optional[UUID]
    
    # Timeline
    acknowledged_at: Optional[datetime]
    remediation_deadline: Optional[datetime]
    resolved_at: Optional[datetime]
    
    # Bounty
    bounty_amount: Optional[Decimal]
    bounty_status: Optional[str]
    
    # Metadata
    submitted_at: datetime
    updated_at: datetime
    last_activity_at: datetime
    closed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ReportDetailResponse(ReportResponse):
    """Detailed report response with attachments and comments."""
    attachments: List[AttachmentResponse] = []
    comments: List[CommentResponse] = []


class ReportListResponse(BaseModel):
    """Schema for list of reports."""
    reports: List[ReportResponse]
    total: int
    limit: int
    offset: int


class ReportStatistics(BaseModel):
    """Schema for report statistics."""
    total: int
    new: int
    triaged: int
    valid: int
    invalid: int
    duplicate: int
    resolved: int


class StatusHistoryResponse(BaseModel):
    """Schema for status history."""
    id: UUID
    report_id: UUID
    from_status: Optional[str]
    to_status: str
    change_reason: Optional[str]
    changed_by: UUID
    changed_at: datetime
    
    class Config:
        from_attributes = True
