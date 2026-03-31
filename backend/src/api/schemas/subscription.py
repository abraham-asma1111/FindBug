"""
Subscription API Schemas - Fixed for proper validation
"""

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional, Any
from datetime import datetime
from uuid import UUID

class SubscriptionCreate(BaseModel):
    """Schema for creating subscription"""
    organization_id: UUID = Field(..., description="Organization ID")
    tier: str = Field(..., regex="^(basic|professional|enterprise)$")
    billing_cycle: str = Field(..., regex="^(monthly|yearly)$")
    
    @validator('tier')
    def validate_tier(cls, v):
        allowed = ['basic', 'professional', 'enterprise']
        if v not in allowed:
            raise ValueError(f'Tier must be one of: {", ".join(allowed)}')
        return v
    
    @validator('billing_cycle')
    def validate_billing_cycle(cls, v):
        allowed = ['monthly', 'yearly']
        if v not in allowed:
            raise ValueError(f'Billing cycle must be one of: {", ".join(allowed)}')
        return v

class SubscriptionResponse(BaseModel):
    """Schema for subscription response"""
    id: UUID
    organization_id: UUID
    tier: str
    status: str
    billing_cycle: str
    price: float
    commission_rate: float
    started_at: datetime
    expires_at: datetime
    auto_renew: bool

    class Config:
        from_attributes = True

class CommissionCalculation(BaseModel):
    """Schema for commission calculation"""
    bounty_amount: float = Field(..., ge=0)
    commission_rate: float = Field(..., ge=0, le=1)
    
    @validator('bounty_amount')
    def validate_bounty_amount(cls, v):
        if v <= 0:
            raise ValueError('Bounty amount must be positive')
        return v
    
    @validator('commission_rate')
    def validate_commission_rate(cls, v):
        if not 0 <= v <= 1:
            raise ValueError('Commission rate must be between 0 and 1')
        return v
