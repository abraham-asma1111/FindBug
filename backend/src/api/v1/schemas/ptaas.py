"""
PTaaS Pydantic Schemas
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
from enum import Enum


class TestingMethodologyEnum(str, Enum):
    OWASP = "OWASP"
    PTES = "PTES"
    NIST = "NIST"
    OSSTMM = "OSSTMM"
    ISSAF = "ISSAF"
    CUSTOM = "CUSTOM"


class PricingModelEnum(str, Enum):
    FIXED = "FIXED"
    SUBSCRIPTION = "SUBSCRIPTION"


class EngagementStatusEnum(str, Enum):
    DRAFT = "DRAFT"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    ACTIVE = "ACTIVE"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    ON_HOLD = "ON_HOLD"


# Engagement Schemas
class PTaaSEngagementCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = None
    scope: Dict[str, Any] = Field(..., description="Targets, exclusions, constraints")
    testing_methodology: TestingMethodologyEnum
    custom_methodology_details: Optional[str] = None
    start_date: datetime
    end_date: datetime
    compliance_requirements: Optional[List[str]] = None
    compliance_notes: Optional[str] = None
    deliverables: Dict[str, Any] = Field(..., description="Reports, documentation, presentations")
    pricing_model: PricingModelEnum
    base_price: Decimal = Field(..., gt=0)
    platform_commission_rate: Decimal = Field(default=15.00, ge=0, le=100)
    team_size: int = Field(default=1, ge=1)
    subscription_interval: Optional[str] = None
    
    @validator('end_date')
    def end_date_after_start(cls, v, values):
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('end_date must be after start_date')
        return v


class PTaaSEngagementUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    scope: Optional[Dict[str, Any]] = None
    testing_methodology: Optional[TestingMethodologyEnum] = None
    custom_methodology_details: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    compliance_requirements: Optional[List[str]] = None
    compliance_notes: Optional[str] = None
    deliverables: Optional[Dict[str, Any]] = None
    status: Optional[EngagementStatusEnum] = None
    assigned_researchers: Optional[List[int]] = None
    team_size: Optional[int] = None


class PTaaSEngagementResponse(BaseModel):
    id: int
    organization_id: int
    name: str
    description: Optional[str]
    status: str
    scope: Dict[str, Any]
    testing_methodology: str
    custom_methodology_details: Optional[str]
    start_date: datetime
    end_date: datetime
    duration_days: Optional[int]
    compliance_requirements: Optional[List[str]]
    compliance_notes: Optional[str]
    deliverables: Dict[str, Any]
    pricing_model: str
    base_price: Decimal
    platform_commission_rate: Decimal
    platform_commission_amount: Optional[Decimal]
    total_price: Optional[Decimal]
    subscription_interval: Optional[str]
    subscription_start_date: Optional[datetime]
    subscription_end_date: Optional[datetime]
    assigned_researchers: Optional[List[int]]
    team_size: int
    created_at: datetime
    updated_at: Optional[datetime]
    created_by: Optional[int]
    
    class Config:
        from_attributes = True


# Finding Schemas
class PTaaSFindingCreate(BaseModel):
    engagement_id: int
    title: str = Field(..., min_length=3, max_length=255)
    description: str = Field(..., min_length=10)
    severity: str = Field(..., pattern="^(Critical|High|Medium|Low|Info)$")
    cvss_score: Optional[Decimal] = Field(None, ge=0, le=10)
    affected_component: Optional[str] = None
    reproduction_steps: Optional[str] = None
    remediation: Optional[str] = None
    references: Optional[List[str]] = None


class PTaaSFindingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[str] = None
    cvss_score: Optional[Decimal] = None
    affected_component: Optional[str] = None
    reproduction_steps: Optional[str] = None
    remediation: Optional[str] = None
    references: Optional[List[str]] = None
    status: Optional[str] = None


class PTaaSFindingResponse(BaseModel):
    id: int
    engagement_id: int
    title: str
    description: str
    severity: str
    cvss_score: Optional[Decimal]
    affected_component: Optional[str]
    reproduction_steps: Optional[str]
    remediation: Optional[str]
    references: Optional[List[str]]
    status: str
    discovered_by: Optional[int]
    discovered_at: datetime
    
    class Config:
        from_attributes = True


# Deliverable Schemas
class PTaaSDeliverableCreate(BaseModel):
    engagement_id: int
    deliverable_type: str = Field(..., pattern="^(report|documentation|presentation)$")
    title: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = None
    file_path: Optional[str] = None
    file_url: Optional[str] = None
    version: str = Field(default="1.0")


class PTaaSDeliverableResponse(BaseModel):
    id: int
    engagement_id: int
    deliverable_type: str
    title: str
    description: Optional[str]
    file_path: Optional[str]
    file_url: Optional[str]
    version: str
    submitted_by: Optional[int]
    submitted_at: datetime
    approved: bool
    approved_by: Optional[int]
    approved_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# Progress Update Schemas
class PTaaSProgressUpdateCreate(BaseModel):
    engagement_id: int
    update_text: str = Field(..., min_length=10)
    progress_percentage: int = Field(default=0, ge=0, le=100)


class PTaaSProgressUpdateResponse(BaseModel):
    id: int
    engagement_id: int
    update_text: str
    progress_percentage: int
    created_by: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True
