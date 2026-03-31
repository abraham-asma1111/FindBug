"""
Authentication Schemas - Pydantic models for request/response validation
Aligned with Extended ERD
"""
from pydantic import BaseModel, EmailStr, Field, HttpUrl, field_validator
from typing import Optional


class RegisterResearcherRequest(BaseModel):
    """Request schema for researcher registration - matches frontend form"""
    # Required fields from frontend form
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    password_confirm: str = Field(..., min_length=8, max_length=128)
    
    @field_validator('password_confirm')
    @classmethod
    def passwords_match(cls, v, info):
        if 'password' in info.data and v != info.data['password']:
            raise ValueError('Passwords do not match')
        return v


class RegisterOrganizationRequest(BaseModel):
    """Request schema for organization registration - matches frontend form"""
    # Required fields from frontend form
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    company_name: str = Field(..., min_length=2, max_length=200)
    phone_number: Optional[str] = Field(None, max_length=20)
    password: str = Field(..., min_length=8, max_length=128)
    password_confirm: str = Field(..., min_length=8, max_length=128)
    
    @field_validator('password_confirm')
    @classmethod
    def passwords_match(cls, v, info):
        if 'password' in info.data and v != info.data['password']:
            raise ValueError('Passwords do not match')
        return v


class LoginRequest(BaseModel):
    """Request schema for login"""
    email: EmailStr
    password: str
    mfa_code: Optional[str] = Field(None, min_length=6, max_length=6, description="MFA code if enabled")


class TokenResponse(BaseModel):
    """Response schema for authentication token"""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str
    user_id: str
    email: str
    role: str
    mfa_required: Optional[bool] = Field(None, description="True if MFA code is required")
    mfa_enabled: Optional[bool] = Field(None, description="True if user has MFA enabled")


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



class RefreshTokenRequest(BaseModel):
    """Request schema for refreshing access token"""
    refresh_token: str


class RefreshTokenResponse(BaseModel):
    """Response schema for refresh token"""
    access_token: str
    refresh_token: str
    token_type: str


class ForgotPasswordRequest(BaseModel):
    """Request schema for forgot password"""
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Request schema for password reset"""
    token: str
    new_password: str = Field(..., min_length=8, max_length=128)


class ChangePasswordRequest(BaseModel):
    """Request schema for password change"""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)


class MessageResponse(BaseModel):
    """Generic message response"""
    message: str


# KYC Schemas
class StartKYCResponse(BaseModel):
    """Response for starting KYC verification"""
    inquiry_id: str
    session_token: str
    status: str
    message: str

class KYCStatusResponse(BaseModel):
    """Response for KYC status check"""
    kyc_status: str
    inquiry_id: Optional[str] = None
    document_type: Optional[str] = None
    verified_at: Optional[str] = None
    message: str

class PersonaWebhookRequest(BaseModel):
    """Persona webhook payload"""
    data: dict
