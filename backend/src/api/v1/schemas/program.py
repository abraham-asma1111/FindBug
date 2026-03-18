"""Program API Schemas."""
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, validator


# Scope Schemas
class ScopeCreate(BaseModel):
    """Schema for creating a program scope."""
    asset_type: str = Field(..., description="Type of asset (domain, api, mobile_app, web_app, other)")
    asset_identifier: str = Field(..., description="Asset identifier (e.g., example.com)")
    is_in_scope: bool = Field(True, description="Whether asset is in scope")
    description: Optional[str] = Field(None, description="Scope description")
    max_severity: Optional[str] = Field(None, description="Maximum severity (critical, high, medium, low)")


class ScopeResponse(BaseModel):
    """Schema for scope response."""
    id: UUID
    program_id: UUID
    asset_type: str
    asset_identifier: str
    is_in_scope: bool
    description: Optional[str]
    max_severity: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Reward Tier Schemas
class RewardTierCreate(BaseModel):
    """Schema for creating a reward tier."""
    severity: str = Field(..., description="Severity level (critical, high, medium, low)")
    min_amount: Decimal = Field(..., description="Minimum reward amount")
    max_amount: Decimal = Field(..., description="Maximum reward amount")
    
    @validator('max_amount')
    def validate_amounts(cls, v, values):
        if 'min_amount' in values and v <= values['min_amount']:
            raise ValueError('max_amount must be greater than min_amount')
        return v


class RewardTierResponse(BaseModel):
    """Schema for reward tier response."""
    id: UUID
    program_id: UUID
    severity: str
    min_amount: Decimal
    max_amount: Decimal
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Program Schemas
class ProgramCreate(BaseModel):
    """Schema for creating a bounty program."""
    name: str = Field(..., min_length=3, max_length=200, description="Program name")
    description: Optional[str] = Field(None, description="Program description")
    type: str = Field(..., description="Program type (bounty or vdp)")
    visibility: str = Field("private", description="Visibility (private or public)")
    budget: Optional[Decimal] = Field(None, description="Program budget")
    policy: Optional[str] = Field(None, description="Security policy")
    rules_of_engagement: Optional[str] = Field(None, description="Rules of engagement")
    safe_harbor: Optional[str] = Field(None, description="Safe harbor policy")
    response_sla_hours: int = Field(72, description="Response SLA in hours")
    
    @validator('type')
    def validate_type(cls, v):
        if v not in ['bounty', 'vdp']:
            raise ValueError('Type must be bounty or vdp')
        return v
    
    @validator('visibility')
    def validate_visibility(cls, v):
        if v not in ['private', 'public']:
            raise ValueError('Visibility must be private or public')
        return v


class ProgramUpdate(BaseModel):
    """Schema for updating a bounty program."""
    name: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = None
    budget: Optional[Decimal] = None
    policy: Optional[str] = None
    rules_of_engagement: Optional[str] = None
    safe_harbor: Optional[str] = None
    response_sla_hours: Optional[int] = None
    status: Optional[str] = None
    
    @validator('status')
    def validate_status(cls, v):
        if v and v not in ['draft', 'private', 'public', 'paused', 'closed']:
            raise ValueError('Invalid status')
        return v


class ProgramResponse(BaseModel):
    """Schema for program response."""
    id: UUID
    organization_id: UUID
    name: str
    description: Optional[str]
    type: str
    status: str
    visibility: str
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    budget: Optional[Decimal]
    policy: Optional[str]
    rules_of_engagement: Optional[str]
    safe_harbor: Optional[str]
    response_sla_hours: int
    created_at: datetime
    updated_at: datetime
    scopes: List[ScopeResponse] = []
    reward_tiers: List[RewardTierResponse] = []
    
    class Config:
        from_attributes = True


class ProgramListResponse(BaseModel):
    """Schema for program list item."""
    id: UUID
    organization_id: UUID
    name: str
    description: Optional[str]
    type: str
    status: str
    visibility: str
    budget: Optional[Decimal]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Invitation Schemas
class InvitationCreate(BaseModel):
    """Schema for creating a program invitation."""
    researcher_id: UUID = Field(..., description="Researcher to invite")
    message: Optional[str] = Field(None, description="Invitation message")
    expires_in_days: int = Field(30, description="Days until invitation expires")


class InvitationResponse(BaseModel):
    """Schema for invitation response."""
    id: UUID
    program_id: UUID
    researcher_id: UUID
    status: str
    invited_by: UUID
    message: Optional[str]
    invited_at: datetime
    responded_at: Optional[datetime]
    expires_at: datetime
    
    class Config:
        from_attributes = True


class InvitationRespond(BaseModel):
    """Schema for responding to an invitation."""
    accept: bool = Field(..., description="Accept or decline invitation")


# Bulk Operations
class BulkRewardTiersCreate(BaseModel):
    """Schema for creating multiple reward tiers."""
    tiers: List[RewardTierCreate] = Field(..., description="List of reward tiers")
