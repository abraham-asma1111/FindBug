"""
Authentication Schemas - Pydantic models for request/response validation
Aligned with Extended ERD
"""
from pydantic import BaseModel, EmailStr, Field, HttpUrl
from typing import Optional


class RegisterResearcherRequest(BaseModel):
    """Request schema for researcher registration - Bugcrowd 2026 Enhanced"""
    # Basic Authentication
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    
    # Bugcrowd 2026 Identity (Required)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    username: str = Field(..., min_length=3, max_length=50, pattern=r'^[a-zA-Z0-9_-]+$')
    
    # Extended ERD Profile (Optional)
    bio: Optional[str] = Field(None, max_length=5000)
    website: Optional[str] = Field(None, max_length=500)
    github: Optional[str] = Field(None, max_length=255)
    twitter: Optional[str] = Field(None, max_length=255)
    
    # Bugcrowd 2026 Professional (Optional)
    linkedin: Optional[str] = Field(None, max_length=255)
    skills: Optional[list[str]] = Field(None, description="List of security skills")


class RegisterOrganizationRequest(BaseModel):
    """Request schema for organization registration - Bugcrowd 2026 Enhanced"""
    # Basic Authentication
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    
    # Extended ERD Company Info (Required)
    company_name: str = Field(..., min_length=2, max_length=200)
    
    # Extended ERD Company Info (Optional)
    industry: Optional[str] = Field(None, max_length=100)
    website: Optional[str] = Field(None, max_length=500)
    subscription_type: Optional[str] = Field(None, max_length=20)
    
    # Bugcrowd 2026 Business Verification (Optional)
    tax_id: Optional[str] = Field(None, max_length=100)
    business_license_url: Optional[str] = Field(None, max_length=500)


class LoginRequest(BaseModel):
    """Request schema for login"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Response schema for authentication token"""
    access_token: str
    token_type: str
    user_id: str
    email: str
    role: str


class RegisterResponse(BaseModel):
    """Response schema for registration"""
    user_id: str
    email: str
    message: str
    researcher_id: Optional[str] = None
    organization_id: Optional[str] = None
    username: Optional[str] = None  # For researchers
    ninja_email: Optional[str] = None  # For researchers



class VerifyEmailRequest(BaseModel):
    """Request schema for email verification"""
    token: str


class ResendVerificationRequest(BaseModel):
    """Request schema for resending verification email"""
    email: EmailStr


class EnableMFAResponse(BaseModel):
    """Response schema for MFA enablement"""
    secret: str
    qr_uri: str
    backup_codes: list[str]
    message: str


class VerifyMFARequest(BaseModel):
    """Request schema for MFA verification"""
    code: str = Field(..., min_length=6, max_length=6)


class DisableMFARequest(BaseModel):
    """Request schema for disabling MFA"""
    password: str


class MFAStatusResponse(BaseModel):
    """Response schema for MFA status"""
    mfa_enabled: bool
    message: str
