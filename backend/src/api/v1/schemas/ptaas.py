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


# Finding Schemas - FREQ-35: Structured Templates
class PTaaSFindingCreate(BaseModel):
    """Structured finding submission with mandatory fields - FREQ-35"""
    engagement_id: int
    title: str = Field(..., min_length=3, max_length=255)
    description: str = Field(..., min_length=10)
    severity: str = Field(..., pattern="^(Critical|High|Medium|Low|Info)$")
    cvss_score: Optional[Decimal] = Field(None, ge=0, le=10)
    affected_component: str = Field(..., min_length=1, description="Mandatory: Component/system affected")
    
    # Mandatory: Proof of Exploit - FREQ-35
    proof_of_exploit: str = Field(..., min_length=50, description="Mandatory: Detailed proof of exploit")
    exploit_code: Optional[str] = Field(None, description="Exploit code/payload used")
    exploit_screenshots: Optional[List[str]] = Field(None, description="URLs to screenshot evidence")
    exploit_video_url: Optional[str] = Field(None, max_length=500, description="Video demonstration URL")
    
    # Mandatory: Impact Analysis - FREQ-35
    impact_analysis: str = Field(..., min_length=50, description="Mandatory: Detailed impact analysis")
    business_impact: str = Field(..., pattern="^(Critical|High|Medium|Low)$", description="Business impact level")
    technical_impact: Dict[str, Any] = Field(..., description="Technical impact details (CIA triad)")
    affected_users: Optional[str] = Field(None, max_length=100, description="User scope affected")
    data_at_risk: Optional[str] = Field(None, description="Data types at risk")
    
    # Mandatory: Remediation Recommendations - FREQ-35
    remediation: str = Field(..., min_length=50, description="Mandatory: Detailed remediation steps")
    remediation_priority: str = Field(..., pattern="^(Immediate|High|Medium|Low)$")
    remediation_effort: str = Field(..., pattern="^(Low|Medium|High|Very High)$")
    remediation_steps: List[str] = Field(..., min_items=1, description="Step-by-step remediation")
    code_fix_example: Optional[str] = Field(None, description="Example code fix")
    
    # Vulnerability Classification
    vulnerability_type: str = Field(..., max_length=100, description="Vulnerability category")
    cwe_id: Optional[str] = Field(None, max_length=50, description="CWE identifier")
    owasp_category: Optional[str] = Field(None, max_length=100, description="OWASP Top 10 category")
    
    # Attack Vector Details (CVSS metrics)
    attack_vector: Optional[str] = Field(None, pattern="^(Network|Adjacent|Local|Physical)$")
    attack_complexity: Optional[str] = Field(None, pattern="^(Low|High)$")
    privileges_required: Optional[str] = Field(None, pattern="^(None|Low|High)$")
    user_interaction: Optional[str] = Field(None, pattern="^(None|Required)$")
    
    # Additional fields
    reproduction_steps: str = Field(..., min_length=20, description="Mandatory: Reproduction steps")
    references: Optional[List[str]] = None
    
    @validator('technical_impact')
    def validate_technical_impact(cls, v):
        """Ensure CIA triad is documented"""
        required_keys = ['confidentiality', 'integrity', 'availability']
        if not all(key in v for key in required_keys):
            raise ValueError(f'technical_impact must include: {", ".join(required_keys)}')
        return v


class PTaaSFindingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[str] = None
    cvss_score: Optional[Decimal] = None
    affected_component: Optional[str] = None
    proof_of_exploit: Optional[str] = None
    exploit_code: Optional[str] = None
    exploit_screenshots: Optional[List[str]] = None
    exploit_video_url: Optional[str] = None
    impact_analysis: Optional[str] = None
    business_impact: Optional[str] = None
    technical_impact: Optional[Dict[str, Any]] = None
    affected_users: Optional[str] = None
    data_at_risk: Optional[str] = None
    remediation: Optional[str] = None
    remediation_priority: Optional[str] = None
    remediation_effort: Optional[str] = None
    remediation_steps: Optional[List[str]] = None
    code_fix_example: Optional[str] = None
    vulnerability_type: Optional[str] = None
    cwe_id: Optional[str] = None
    owasp_category: Optional[str] = None
    attack_vector: Optional[str] = None
    attack_complexity: Optional[str] = None
    privileges_required: Optional[str] = None
    user_interaction: Optional[str] = None
    reproduction_steps: Optional[str] = None
    references: Optional[List[str]] = None
    status: Optional[str] = None
    retest_notes: Optional[str] = None


class PTaaSFindingResponse(BaseModel):
    id: int
    engagement_id: int
    title: str
    description: str
    severity: str
    cvss_score: Optional[Decimal]
    affected_component: Optional[str]
    
    # Proof of Exploit
    proof_of_exploit: Optional[str]
    exploit_code: Optional[str]
    exploit_screenshots: Optional[List[str]]
    exploit_video_url: Optional[str]
    
    # Impact Analysis
    impact_analysis: Optional[str]
    business_impact: Optional[str]
    technical_impact: Optional[Dict[str, Any]]
    affected_users: Optional[str]
    data_at_risk: Optional[str]
    
    # Remediation
    remediation: Optional[str]
    remediation_priority: Optional[str]
    remediation_effort: Optional[str]
    remediation_steps: Optional[List[str]]
    code_fix_example: Optional[str]
    
    # Classification
    vulnerability_type: Optional[str]
    cwe_id: Optional[str]
    owasp_category: Optional[str]
    
    # Attack Vector
    attack_vector: Optional[str]
    attack_complexity: Optional[str]
    privileges_required: Optional[str]
    user_interaction: Optional[str]
    
    # Validation
    validated: Optional[bool]
    validated_by: Optional[int]
    validated_at: Optional[datetime]
    retest_required: Optional[bool]
    retest_notes: Optional[str]
    
    # Template
    template_version: Optional[str]
    mandatory_fields_complete: Optional[bool]
    
    reproduction_steps: Optional[str]
    references: Optional[List[str]]
    status: str
    discovered_by: Optional[int]
    discovered_at: datetime
    
    class Config:
        from_attributes = True


class PTaaSFindingValidation(BaseModel):
    """Schema for validating a finding"""
    validated: bool
    retest_required: bool = False
    retest_notes: Optional[str] = None


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
