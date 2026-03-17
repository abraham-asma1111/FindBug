"""
Authentication Endpoints - API routes for user authentication
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.security import SecurityAudit, InputSanitization
from src.services.auth_service import AuthService
from src.domain.models.user import User
from src.domain.repositories import UserRepository, ResearcherRepository, OrganizationRepository
from src.api.v1.middlewares import get_current_user, get_current_verified_user
from src.api.v1.schemas.auth import (
    RegisterResearcherRequest,
    RegisterOrganizationRequest,
    LoginRequest,
    TokenResponse,
    RegisterResponse,
    VerifyEmailRequest,
    ResendVerificationRequest,
    EnableMFAResponse,
    VerifyMFARequest,
    DisableMFARequest,
    MFAStatusResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    ChangePasswordRequest,
    MessageResponse
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    """Dependency to get AuthService instance"""
    user_repo = UserRepository(db)
    researcher_repo = ResearcherRepository(db)
    organization_repo = OrganizationRepository(db)
    return AuthService(user_repo, researcher_repo, organization_repo)


@router.post(
    "/register/researcher",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register as Researcher",
    description="Register a new security researcher account - Extended ERD"
)
async def register_researcher(
    data: RegisterResearcherRequest,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Register a new researcher account.
    
    Requirements:
    - Valid email address
    - Password: min 8 chars, uppercase, lowercase, digit, special char
    - Optional: bio, website, github, twitter
    """
    try:
        result = auth_service.register_researcher(
            email=data.email,
            password=data.password,
            first_name=data.first_name,
            last_name=data.last_name,
            username=data.username,
            bio=data.bio,
            website=data.website,
            github=data.github,
            twitter=data.twitter,
            linkedin=data.linkedin,
            skills=data.skills
        )
        
        # Log registration
        SecurityAudit.log_security_event(
            "USER_REGISTRATION",
            result["user_id"],
            {"role": "researcher", "email": data.email},
            request
        )
        
        return RegisterResponse(**result)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Log error
        SecurityAudit.log_security_event(
            "REGISTRATION_ERROR",
            None,
            {"error": str(e), "role": "researcher"},
            request
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again."
        )


@router.post(
    "/register/organization",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register as Organization",
    description="Register a new organization account - Extended ERD"
)
async def register_organization(
    data: RegisterOrganizationRequest,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Register a new organization account.
    
    Requirements:
    - Valid email address
    - Password: min 8 chars, uppercase, lowercase, digit, special char
    - Company name: min 2 chars
    - Optional: industry, website, subscription_type
    """
    try:
        result = auth_service.register_organization(
            email=data.email,
            password=data.password,
            company_name=data.company_name,
            industry=data.industry,
            website=data.website,
            subscription_type=data.subscription_type,
            tax_id=data.tax_id,
            business_license_url=data.business_license_url
        )
        
        # Log registration
        SecurityAudit.log_security_event(
            "USER_REGISTRATION",
            result["user_id"],
            {"role": "organization", "email": data.email},
            request
        )
        
        return RegisterResponse(**result)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Log error
        SecurityAudit.log_security_event(
            "REGISTRATION_ERROR",
            None,
            {"error": str(e), "role": "organization"},
            request
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again."
        )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="User Login",
    description="Authenticate user and receive JWT token"
)
async def login(
    data: LoginRequest,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    User login endpoint.
    
    Returns JWT access token on successful authentication.
    
    Security features:
    - Account lockout after 5 failed attempts (30 minutes)
    - Failed login attempt tracking
    - Security event logging
    """
    try:
        result = auth_service.login(
            email=data.email,
            password=data.password,
            mfa_code=data.mfa_code,
            request=request
        )
        
        return TokenResponse(**result)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )
    except Exception as e:
        # Log error
        SecurityAudit.log_security_event(
            "LOGIN_ERROR",
            None,
            {"error": str(e), "email": data.email},
            request
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed. Please try again."
        )



@router.post(
    "/verify-email",
    summary="Verify Email Address",
    description="Verify user email with token from email"
)
async def verify_email(
    data: VerifyEmailRequest,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Verify email address with token"""
    try:
        result = auth_service.verify_email(data.token)
        
        # Log verification
        SecurityAudit.log_security_event(
            "EMAIL_VERIFIED",
            None,
            {"email": result.get("email")},
            request
        )
        
        return result
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Email verification failed. Please try again."
        )


@router.post(
    "/resend-verification",
    summary="Resend Verification Email",
    description="Resend email verification link"
)
async def resend_verification(
    data: ResendVerificationRequest,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Resend verification email"""
    try:
        result = auth_service.resend_verification_email(data.email)
        return result
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send verification email. Please try again."
        )


@router.post(
    "/mfa/enable",
    response_model=EnableMFAResponse,
    summary="Enable MFA",
    description="Enable Multi-Factor Authentication"
)
async def enable_mfa(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
    current_user: User = Depends(get_current_verified_user)
):
    """
    Enable MFA for user account.
    Returns QR code URI and backup codes.
    """
    try:
        result = auth_service.enable_mfa(str(current_user.id))
        
        # Log MFA enablement
        SecurityAudit.log_security_event(
            "MFA_ENABLED",
            str(current_user.id),
            {},
            request
        )
        
        return EnableMFAResponse(**result)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to enable MFA. Please try again."
        )


@router.post(
    "/mfa/verify",
    response_model=MFAStatusResponse,
    summary="Verify MFA Setup",
    description="Verify MFA code to complete setup"
)
async def verify_mfa_setup(
    data: VerifyMFARequest,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
    current_user: User = Depends(get_current_verified_user)
):
    """Verify MFA code to complete MFA setup"""
    try:
        result = auth_service.verify_mfa_setup(str(current_user.id), data.code)
        
        # Log MFA verification
        SecurityAudit.log_security_event(
            "MFA_VERIFIED",
            str(current_user.id),
            {},
            request
        )
        
        return MFAStatusResponse(**result)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="MFA verification failed. Please try again."
        )


@router.post(
    "/mfa/disable",
    response_model=MFAStatusResponse,
    summary="Disable MFA",
    description="Disable Multi-Factor Authentication"
)
async def disable_mfa(
    data: DisableMFARequest,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
    current_user: User = Depends(get_current_verified_user)
):
    """Disable MFA (requires password confirmation)"""
    try:
        result = auth_service.disable_mfa(str(current_user.id), data.password)
        
        # Log MFA disablement
        SecurityAudit.log_security_event(
            "MFA_DISABLED",
            str(current_user.id),
            {},
            request
        )
        
        return MFAStatusResponse(**result)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to disable MFA. Please try again."
        )



@router.post(
    "/refresh",
    response_model=RefreshTokenResponse,
    summary="Refresh Access Token",
    description="Get new access token using refresh token"
)
async def refresh_token(
    data: RefreshTokenRequest,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Refresh access token"""
    try:
        result = auth_service.refresh_access_token(data.refresh_token)
        return RefreshTokenResponse(**result)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        print(f"[ERROR] Refresh token failed: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Token refresh failed: {str(e)}"
        )


@router.post(
    "/forgot-password",
    response_model=MessageResponse,
    summary="Forgot Password",
    description="Request password reset email"
)
async def forgot_password(
    data: ForgotPasswordRequest,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Request password reset"""
    try:
        result = auth_service.forgot_password(data.email)
        return MessageResponse(**result)
    
    except Exception as e:
        # Always return success to prevent email enumeration
        return MessageResponse(message="If the email exists, a password reset link has been sent.")


@router.post(
    "/reset-password",
    response_model=MessageResponse,
    summary="Reset Password",
    description="Reset password using token from email"
)
async def reset_password(
    data: ResetPasswordRequest,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Reset password with token"""
    try:
        result = auth_service.reset_password(data.token, data.new_password)
        
        # Log password reset
        SecurityAudit.log_security_event(
            "PASSWORD_RESET",
            None,
            {},
            request
        )
        
        return MessageResponse(**result)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset failed. Please try again."
        )


@router.post(
    "/change-password",
    response_model=MessageResponse,
    summary="Change Password",
    description="Change password (requires authentication)"
)
async def change_password(
    data: ChangePasswordRequest,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
    current_user: User = Depends(get_current_user)
):
    """Change password (authenticated)"""
    try:
        result = auth_service.change_password(
            str(current_user.id),
            data.current_password,
            data.new_password
        )
        
        # Log password change
        SecurityAudit.log_security_event(
            "PASSWORD_CHANGED",
            str(current_user.id),
            {},
            request
        )
        
        return MessageResponse(**result)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed. Please try again."
        )


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Logout",
    description="Logout user (invalidate refresh token)"
)
async def logout(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
    current_user: User = Depends(get_current_user)
):
    """Logout user"""
    try:
        result = auth_service.logout(str(current_user.id))
        
        # Log logout
        SecurityAudit.log_security_event(
            "LOGOUT",
            str(current_user.id),
            {},
            request
        )
        
        return MessageResponse(**result)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed. Please try again."
        )



# ============================================================================
# KYC ENDPOINTS (Persona Integration)
# ============================================================================

@router.post(
    "/kyc/start",
    response_model=dict,
    summary="Start KYC Verification",
    description="Start Persona KYC verification for researcher (requires email verification)"
)
async def start_kyc_verification(
    request: Request,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """
    Start KYC verification using Persona
    
    Flow:
    1. Create Persona inquiry session
    2. Return inquiry_id and session_token to frontend
    3. Frontend loads Persona SDK with session_token
    4. User completes ID + selfie verification
    5. Persona sends webhook with results
    """
    from src.core.kyc_service import PersonaKYCService
    from src.domain.repositories.researcher_repository import ResearcherRepository
    
    # Only researchers can do KYC
    if current_user.role != "researcher":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="KYC verification is only for researchers"
        )
    
    researcher_repo = ResearcherRepository(db)
    researcher = researcher_repo.get_by_user_id(str(current_user.id))
    
    if not researcher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Researcher profile not found"
        )
    
    # Check if already verified
    if researcher.kyc_status == "verified":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="KYC already verified"
        )
    
    try:
        kyc_service = PersonaKYCService()
        inquiry_data = kyc_service.create_inquiry(
            researcher_id=str(researcher.id),
            email=current_user.email,
            first_name=researcher.first_name,
            last_name=researcher.last_name
        )
        
        # Update researcher with inquiry_id
        researcher.kyc_status = "pending"
        db.commit()
        
        # Log security event
        SecurityAudit.log_event(
            user_id=str(current_user.id),
            event_type="kyc_started",
            ip_address=request.client.host,
            details={"inquiry_id": inquiry_data["inquiry_id"]}
        )
        
        return {
            "inquiry_id": inquiry_data["inquiry_id"],
            "session_token": inquiry_data["session_token"],
            "status": inquiry_data["status"],
            "message": "KYC verification session created. Please complete verification in the Persona widget."
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start KYC verification: {str(e)}"
        )


@router.get(
    "/kyc/status",
    response_model=dict,
    summary="Get KYC Status",
    description="Get current KYC verification status for researcher"
)
async def get_kyc_status(
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """Get KYC verification status"""
    from src.domain.repositories.researcher_repository import ResearcherRepository
    
    if current_user.role != "researcher":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="KYC status is only for researchers"
        )
    
    researcher_repo = ResearcherRepository(db)
    researcher = researcher_repo.get_by_user_id(str(current_user.id))
    
    if not researcher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Researcher profile not found"
        )
    
    return {
        "kyc_status": researcher.kyc_status or "not_started",
        "message": f"KYC status: {researcher.kyc_status or 'not_started'}"
    }


@router.post(
    "/kyc/webhook",
    status_code=status.HTTP_200_OK,
    summary="Persona Webhook",
    description="Webhook endpoint for Persona to send verification results"
)
async def persona_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Receive webhook from Persona when verification completes
    
    Persona sends webhooks for:
    - inquiry.completed - Verification finished
    - inquiry.failed - Verification failed
    - inquiry.expired - Session expired
    """
    from src.core.kyc_service import PersonaKYCService
    from src.domain.repositories.researcher_repository import ResearcherRepository
    
    # Get raw body for signature verification
    body = await request.body()
    signature = request.headers.get("Persona-Signature", "")
    
    # Verify webhook signature
    kyc_service = PersonaKYCService()
    if not kyc_service.verify_webhook_signature(body.decode(), signature):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook signature"
        )
    
    # Parse webhook data
    webhook_data = await request.json()
    result = kyc_service.process_webhook(webhook_data)
    
    # Update researcher KYC status
    researcher_repo = ResearcherRepository(db)
    researcher = researcher_repo.get(result["researcher_id"])
    
    if researcher:
        researcher.kyc_status = result["kyc_status"]
        if result["verified_at"]:
            # Store verification timestamp if needed
            pass
        db.commit()
        
        # Log security event
        SecurityAudit.log_event(
            user_id=str(researcher.user_id),
            event_type="kyc_completed",
            ip_address=request.client.host,
            details={
                "kyc_status": result["kyc_status"],
                "inquiry_id": result["inquiry_id"]
            }
        )
    
    return {"status": "processed"}
