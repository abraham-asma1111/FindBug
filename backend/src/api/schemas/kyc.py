"""
KYC API Schemas - Fixed for proper validation
"""

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional, Any
from datetime import datetime
from uuid import UUID

class KYCSubmission(BaseModel):
    """Schema for KYC document submission"""
    document_type: str = Field(..., regex="^(passport|national_id|drivers_license|residence_permit)$")
    document_number: str = Field(..., min_length=5, max_length=50)
    
    @validator('document_type')
    def validate_document_type(cls, v):
        allowed = ['passport', 'national_id', 'drivers_license', 'residence_permit']
        if v not in allowed:
            raise ValueError(f'Document type must be one of: {", ".join(allowed)}')
        return v
    
    @validator('document_number')
    def validate_document_number(cls, v):
        if not v or len(v.strip()) < 5:
            raise ValueError('Document number must be at least 5 characters')
        return v.strip()

class KYCResponse(BaseModel):
    """Schema for KYC response"""
    id: UUID
    user_id: UUID
    status: str
    document_type: str
    document_number: str
    submitted_at: datetime
    verified_at: Optional[datetime]
    expires_at: Optional[datetime]
    rejection_reason: Optional[str]

    class Config:
        from_attributes = True

class KYCReview(BaseModel):
    """Schema for KYC review"""
    approved: bool = Field(..., description="Whether to approve or reject")
    rejection_reason: Optional[str] = Field(None, max_length=500)
    
    @validator('rejection_reason')
    def validate_rejection_reason(cls, v, values):
        if not values.get('approved') and not v:
            raise ValueError('Rejection reason is required when rejecting KYC')
        return v
