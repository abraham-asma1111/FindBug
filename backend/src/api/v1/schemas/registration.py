"""
Registration API Schemas - OTP-based registration flow
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class InitiateRegistrationRequest(BaseModel):
    """Request to initiate registration"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password")
    first_name: str = Field(..., min_length=1, max_length=100, description="First name")
    last_name: str = Field(..., min_length=1, max_length=100, description="Last name")
    
    # Organization-specific fields (optional for researchers)
    company_name: Optional[str] = Field(None, min_length=2, max_length=200, description="Company name (organizations only)")
    phone_number: Optional[str] = Field(None, max_length=20, description="Phone number (organizations only)")
    country: Optional[str] = Field(None, max_length=100, description="Country (organizations only)")


class InitiateRegistrationResponse(BaseModel):
    """Response from initiate registration"""
    success: bool = Field(..., description="Whether registration was initiated successfully")
    message: str = Field(..., description="Success message")
    email: str = Field(..., description="Email address where OTP was sent")
    verification_method: str = Field(..., description="Verification method (otp)")
    expires_in_minutes: int = Field(..., description="OTP expiration time in minutes")


class VerifyOTPRequest(BaseModel):
    """Request to verify OTP"""
    email: EmailStr = Field(..., description="User email address")
    otp: str = Field(..., min_length=6, max_length=6, description="6-digit OTP code")


class VerifyOTPResponse(BaseModel):
    """Response from OTP verification"""
    success: bool = Field(..., description="Whether verification was successful")
    message: str = Field(..., description="Success message")
    user_id: str = Field(..., description="Created user ID")
    email: str = Field(..., description="User email")
    role: str = Field(..., description="User role (researcher/organization)")
    is_verified: bool = Field(..., description="Whether user is verified")


class VerifyTokenRequest(BaseModel):
    """Request to verify token (backup method)"""
    token: str = Field(..., description="Verification token from email link")


class VerifyTokenResponse(BaseModel):
    """Response from token verification"""
    success: bool = Field(..., description="Whether verification was successful")
    message: str = Field(..., description="Success message")
    user_id: str = Field(..., description="Created user ID")
    email: str = Field(..., description="User email")
    role: str = Field(..., description="User role (researcher/organization)")
    is_verified: bool = Field(..., description="Whether user is verified")


class ResendOTPRequest(BaseModel):
    """Request to resend OTP"""
    email: EmailStr = Field(..., description="User email address")


class ResendOTPResponse(BaseModel):
    """Response from resend OTP"""
    success: bool = Field(..., description="Whether OTP was resent successfully")
    message: str = Field(..., description="Success message")
    expires_in_minutes: int = Field(..., description="OTP expiration time in minutes")