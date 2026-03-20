"""
PTaaS Triage Schemas - FREQ-36
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal


# Triage Schemas
class PTaaSFindingTriageCreate(BaseModel):
    """Schema for triaging a finding - FREQ-36"""
    triage_status: str = Field(..., pattern="^(PENDING|VALIDATED|REJECTED|NEEDS_INFO)$")
    triage_notes: Optional[str] = None
    
    # Prioritization
    priority_score: int = Field(..., ge=1, le=100)
    priority_level: str = Field(..., pattern="^(CRITICAL|HIGH|MEDIUM|LOW)$")
    priority_justification: Optional[str] = None
    
    # Risk assessment
    risk_rating: str = Field(..., pattern="^(CRITICAL|HIGH|MEDIUM|LOW)$")
    likelihood: Optional[str] = Field(None, pattern="^(CERTAIN|LIKELY|POSSIBLE|UNLIKELY)$")
    impact_score: Optional[int] = Field(None, ge=1, le=10)
    exploitability_score: Optional[int] = Field(None, ge=1, le=10)
    
    # Compliance
    compliance_frameworks: Optional[List[str]] = None
    compliance_controls: Optional[List[str]] = None
    regulatory_impact: Optional[str] = None
    
    # Evidence validation
    evidence_validated: bool = False
    evidence_quality: Optional[str] = Field(None, pattern="^(EXCELLENT|GOOD|ADEQUATE|POOR)$")
    evidence_notes: Optional[str] = None
    
    # Recommendations
    recommended_action: Optional[str] = Field(None, pattern="^(IMMEDIATE_FIX|SCHEDULED_FIX|ACCEPT_RISK|FALSE_POSITIVE)$")
    estimated_fix_time: Optional[str] = None
    
    # Executive summary
    executive_summary: Optional[str] = None
    business_context: Optional[str] = None


class PTaaSFindingTriageResponse(BaseModel):
    id: int
    finding_id: int
    triaged_by: int
    triaged_at: datetime
    triage_status: str
    triage_notes: Optional[str]
    priority_score: int
    priority_level: str
    priority_justification: Optional[str]
    risk_rating: str
    likelihood: Optional[str]
    impact_score: Optional[int]
    exploitability_score: Optional[int]
    compliance_frameworks: Optional[List[str]]
    compliance_controls: Optional[List[str]]
    regulatory_impact: Optional[str]
    evidence_validated: bool
    evidence_quality: Optional[str]
    evidence_notes: Optional[str]
    recommended_action: Optional[str]
    estimated_fix_time: Optional[str]
    executive_summary: Optional[str]
    business_context: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Prioritization Schemas
class PTaaSFindingPrioritizationCreate(BaseModel):
    new_priority: str = Field(..., pattern="^(CRITICAL|HIGH|MEDIUM|LOW)$")
    reason: str = Field(..., min_length=10)
    factors_considered: Optional[List[str]] = None


class PTaaSFindingPrioritizationResponse(BaseModel):
    id: int
    finding_id: int
    prioritized_by: int
    prioritized_at: datetime
    old_priority: Optional[str]
    new_priority: str
    reason: str
    factors_considered: Optional[List[str]]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Executive Report Schemas
class PTaaSExecutiveReportCreate(BaseModel):
    report_title: Optional[str] = None
    report_type: str = Field(default="EXECUTIVE", pattern="^(EXECUTIVE|TECHNICAL|COMPLIANCE)$")


class PTaaSExecutiveReportResponse(BaseModel):
    id: int
    engagement_id: int
    report_title: str
    report_type: str
    generated_by: int
    generated_at: datetime
    report_period_start: Optional[datetime]
    report_period_end: Optional[datetime]
    executive_summary: str
    key_findings: Optional[List[Dict[str, Any]]]
    overall_risk_rating: str
    total_findings: int
    critical_findings: int
    high_findings: int
    medium_findings: int
    low_findings: int
    risk_score: Optional[Decimal]
    risk_trend: Optional[str]
    compliance_status: Optional[Dict[str, Any]]
    compliance_gaps: Optional[List[str]]
    compliance_recommendations: Optional[str]
    immediate_actions: Optional[List[str]]
    short_term_actions: Optional[List[str]]
    long_term_actions: Optional[List[str]]
    evidence_summary: Optional[Dict[str, Any]]
    report_file_path: Optional[str]
    report_file_url: Optional[str]
    approved: bool
    approved_by: Optional[int]
    approved_at: Optional[datetime]
    distributed_to: Optional[List[int]]
    distributed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PTaaSPendingTriageResponse(BaseModel):
    finding_id: int
    engagement_id: int
    title: str
    severity: str
    discovered_at: datetime
    has_triage: bool
