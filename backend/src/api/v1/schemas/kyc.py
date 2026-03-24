"""
KYC Schemas — Pydantic models for KYC verification (FREQ-01)
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class KYCSubmissionRequest(BaseModel):
    """Request schema for KYC document submission"""
    document_type: str = Field(
        ...,
        description="Type of document (passport, national_id, drivers_license, residence_permit)"
    )
    document_number: str = Field(..., min_length=1, max_length=100, description="Document identification number")


class KYCStatusResponse(BaseModel):
    """Response schema for KYC status"""
    kyc_id: Optional[str] = None
    status: str
    document_type: Optional[str] = None
    submitted_at: Optional[str] = None
    verified_at: Optional[str] = None
    expires_at: Optional[str] = None
    rejection_reason: Optional[str] = None
    message: str


class KYCSubmissionResponse(BaseModel):
    """Response schema for KYC submission"""
    kyc_id: str
    status: str
    document_type: str
    submitted_at: str
    message: str


class KYCReviewRequest(BaseModel):
    """Request schema for admin KYC review"""
    approved: bool = Field(..., description="True to approve, False to reject")
    rejection_reason: Optional[str] = Field(
        None,
        max_length=1000,
        description="Reason for rejection (required if approved=False)"
    )


class KYCReviewResponse(BaseModel):
    """Response schema for KYC review"""
    kyc_id: str
    user_id: str
    status: str
    verified_by: Optional[str] = None
    verified_at: Optional[str] = None
    rejection_reason: Optional[str] = None
    message: str


class KYCVerificationItem(BaseModel):
    """Single KYC verification item"""
    kyc_id: str
    user_id: str
    user_email: Optional[str] = None
    status: str
    document_type: Optional[str] = None
    document_number: Optional[str] = None
    submitted_at: Optional[str] = None
    verified_at: Optional[str] = None
    verified_by: Optional[str] = None
    rejection_reason: Optional[str] = None
    expires_at: Optional[str] = None
    document_front: Optional[str] = None
    document_back: Optional[str] = None
    selfie_photo: Optional[str] = None


class KYCListResponse(BaseModel):
    """Response schema for KYC list"""
    kyc_verifications: list[KYCVerificationItem]
    total: int
    skip: int
    limit: int


class KYCStatusUpdateRequest(BaseModel):
    """Request schema for KYC status update"""
    status: str = Field(
        ...,
        description="New status (pending, approved, rejected, expired)"
    )


class KYCStatusUpdateResponse(BaseModel):
    """Response schema for KYC status update"""
    kyc_id: str
    status: str
    message: str
