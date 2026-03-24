"""
Security Schemas — Pydantic models for security logging (FREQ-17)
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class SecurityEventResponse(BaseModel):
    """Response schema for security event"""
    event_id: str
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    event_type: str
    severity: str
    description: str
    ip_address: Optional[str] = None
    is_blocked: bool
    created_at: str


class SecurityEventsListResponse(BaseModel):
    """Response schema for security events list"""
    events: List[SecurityEventResponse]
    total: int
    skip: int
    limit: int


class LoginHistoryResponse(BaseModel):
    """Response schema for login history"""
    login_id: str
    user_id: str
    user_email: Optional[str] = None
    is_successful: bool
    failure_reason: Optional[str] = None
    mfa_used: bool
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: str


class LoginHistoryListResponse(BaseModel):
    """Response schema for login history list"""
    logins: List[LoginHistoryResponse]
    total: int
    skip: int
    limit: int


class AuditTrailItem(BaseModel):
    """Single audit trail item"""
    type: str  # "security_event" or "login_attempt"
    id: str
    timestamp: str
    # Security event fields
    event_type: Optional[str] = None
    severity: Optional[str] = None
    description: Optional[str] = None
    is_blocked: Optional[bool] = None
    # Login attempt fields
    is_successful: Optional[bool] = None
    failure_reason: Optional[str] = None
    mfa_used: Optional[bool] = None
    user_agent: Optional[str] = None
    # Common fields
    ip_address: Optional[str] = None


class AuditTrailResponse(BaseModel):
    """Response schema for audit trail"""
    user_id: str
    user_email: str
    audit_trail: List[AuditTrailItem]
    total: int
    skip: int
    limit: int
    days: int


class IncidentReportRequest(BaseModel):
    """Request schema for reporting security incident"""
    incident_type: str = Field(..., min_length=1, max_length=100, description="Type of security incident")
    description: str = Field(..., min_length=10, max_length=2000, description="Detailed description of incident")
    severity: Optional[str] = Field("high", description="Incident severity (low, medium, high, critical)")


class IncidentReportResponse(BaseModel):
    """Response schema for incident report"""
    incident_id: str
    incident_type: str
    severity: str
    status: str
    message: str


class SecurityStatisticsResponse(BaseModel):
    """Response schema for security statistics"""
    period_days: int
    security_events: dict
    login_attempts: dict
