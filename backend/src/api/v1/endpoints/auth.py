"""
Authentication Endpoints - API routes for user authentication
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.security import SecurityAudit, InputSanitization
from src.services.auth_service import AuthService
from src.domain.repositories import UserRepository, ResearcherRepository, OrganizationRepository
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
    MFAStatusResponse
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
    current_user_id: str = None  # TODO: Get from JWT token
):
    """
    Enable MFA for user account.
    Returns QR code URI and backup codes.
    """
    try:
        # TODO: Extract user_id from JWT token
        # For now, using a placeholder
        if not current_user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        result = auth_service.enable_mfa(current_user_id)
        
        # Log MFA enablement
        SecurityAudit.log_security_event(
            "MFA_ENABLED",
            current_user_id,
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
    current_user_id: str = None  # TODO: Get from JWT token
):
    """Verify MFA code to complete MFA setup"""
    try:
        if not current_user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        result = auth_service.verify_mfa_setup(current_user_id, data.code)
        
        # Log MFA verification
        SecurityAudit.log_security_event(
            "MFA_VERIFIED",
            current_user_id,
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
    current_user_id: str = None  # TODO: Get from JWT token
):
    """Disable MFA (requires password confirmation)"""
    try:
        if not current_user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        result = auth_service.disable_mfa(current_user_id, data.password)
        
        # Log MFA disablement
        SecurityAudit.log_security_event(
            "MFA_DISABLED",
            current_user_id,
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
