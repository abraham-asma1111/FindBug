"""
AI Red Teaming API Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from decimal import Decimal


class EngagementCreate(BaseModel):
    """Schema for creating AI Red Teaming engagement"""
    name: str = Field(..., min_length=3, max_length=255)
    target_ai_system: str = Field(..., max_length=255)
    model_type: str = Field(..., pattern="^(llm|ml_model|ai_agent|chatbot|recommendation_system|computer_vision)$")
    testing_environment: str = Field(..., max_length=500)
    ethical_guidelines: str
    scope_description: Optional[str] = None
    allowed_attack_types: Optional[List[str]] = None


class EngagementResponse(BaseModel):
    """Schema for engagement response"""
    id: UUID
    organization_id: UUID
    name: str
    target_ai_system: str
    model_type: str
    testing_environment: str
    ethical_guidelines: str
    scope_description: Optional[str]
    allowed_attack_types: Optional[List[str]]
    status: str
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    assigned_experts: Optional[List[str]]
    total_findings: int
    critical_findings: int
    high_findings: int
    medium_findings: int
    low_findings: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TestingEnvironmentCreate(BaseModel):
    """Schema for creating testing environment"""
    model_type: str
    sandbox_url: str
    api_endpoint: str
    access_token: str
    access_controls: Dict[str, Any]
    rate_limits: Optional[Dict[str, Any]] = None
    is_isolated: bool = True


class TestingEnvironmentResponse(BaseModel):
    """Schema for testing environment response"""
    id: UUID
    engagement_id: UUID
    model_type: str
    sandbox_url: str
    api_endpoint: str
    access_controls: Dict[str, Any]
    rate_limits: Optional[Dict[str, Any]]
    is_isolated: bool
    monitoring_enabled: bool
    log_all_interactions: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class VulnerabilityReportCreate(BaseModel):
    """Schema for creating AI vulnerability report"""
    title: str = Field(..., min_length=3, max_length=255)
    input_prompt: str
    model_response: str
    attack_type: str
    severity: str = Field(..., pattern="^(critical|high|medium|low)$")
    impact: str
    reproduction_steps: str
    mitigation_recommendation: Optional[str] = None
    model_version: Optional[str] = None
    environment_details: Optional[Dict[str, Any]] = None


class VulnerabilityReportResponse(BaseModel):
    """Schema for vulnerability report response"""
    id: UUID
    engagement_id: UUID
    researcher_id: UUID
    title: str
    input_prompt: str
    model_response: str
    attack_type: str
    classification: Optional[str]
    severity: str
    impact: str
    reproduction_steps: str
    mitigation_recommendation: Optional[str]
    model_version: Optional[str]
    environment_details: Optional[Dict[str, Any]]
    status: str
    submitted_at: datetime
    validated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class FindingClassificationCreate(BaseModel):
    """Schema for classifying finding"""
    primary_category: str = Field(..., pattern="^(security|safety|trust|privacy|fairness|reliability)$")
    risk_score: Decimal = Field(..., ge=0, le=100)
    confidence_level: Decimal = Field(..., ge=0, le=100)
    justification: str
    secondary_categories: Optional[List[str]] = None
    affected_components: Optional[Dict[str, Any]] = None
    remediation_priority: Optional[str] = None


class FindingClassificationResponse(BaseModel):
    """Schema for finding classification response"""
    id: UUID
    report_id: UUID
    primary_category: str
    secondary_categories: Optional[List[str]]
    risk_score: Optional[Decimal]
    confidence_level: Optional[Decimal]
    classified_by: Optional[UUID]
    classified_at: datetime
    justification: str
    affected_components: Optional[Dict[str, Any]]
    remediation_priority: Optional[str]
    
    class Config:
        from_attributes = True


class SecurityReportCreate(BaseModel):
    """Schema for creating security report"""
    report_title: str
    executive_summary: Optional[str] = None
    recommendations: Optional[str] = None


class SecurityReportResponse(BaseModel):
    """Schema for security report response"""
    id: UUID
    engagement_id: UUID
    report_title: str
    generated_by: Optional[UUID]
    total_findings: int
    security_findings: int
    safety_findings: int
    trust_findings: int
    privacy_findings: int
    fairness_findings: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    executive_summary: Optional[str]
    key_findings: Optional[List[Dict[str, Any]]]
    recommendations: Optional[str]
    generated_at: datetime
    report_file_url: Optional[str]
    
    class Config:
        from_attributes = True


class AssignExpertsRequest(BaseModel):
    """Schema for assigning experts"""
    researcher_ids: List[UUID] = Field(..., min_items=1)


class ValidateFindingRequest(BaseModel):
    """Schema for validating finding"""
    is_valid: bool


class EngagementStatusUpdate(BaseModel):
    """Schema for updating engagement status"""
    status: str = Field(..., pattern="^(draft|pending|active|completed|archived)$")
