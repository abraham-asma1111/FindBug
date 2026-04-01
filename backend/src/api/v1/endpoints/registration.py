"""
Registration Endpoints - OTP-based registration flow
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.security import SecurityAudit
from src.services.registration_service import RegistrationService
from src.domain.repositories.pending_registration_repository import PendingRegistrationRepository
from src.domain.repositories import UserRepository, ResearcherRepository, OrganizationRepository
from src.api.v1.schemas.registration import (
    InitiateRegistrationRequest,
    InitiateRegistrationResponse,
    VerifyOTPRequest,
    VerifyOTPResponse,
    ResendOTPRequest,
    ResendOTPResponse,
    VerifyTokenRequest,
    VerifyTokenResponse
)

router = APIRouter(prefix="/registration", tags=["Registration"])


def get_registration_service(db: Session = Depends(get_db)) -> RegistrationService:
    """Dependency to get RegistrationService instance"""
    pending_repo = PendingRegistrationRepository(db)
    user_repo = UserRepository(db)
    researcher_repo = ResearcherRepository(db)
    organization_repo = OrganizationRepository(db)
    return RegistrationService(pending_repo, user_repo, researcher_repo, organization_repo, db)


@router.post(
    "/researcher/initiate",
    response_model=InitiateRegistrationResponse,
    status_code=status.HTTP_200_OK,
    summary="Initiate Researcher Registration",
    description="Start researcher registration - sends OTP to email"
)
async def initiate_researcher_registration(
    data: InitiateRegistrationRequest,
    request: Request,
    registration_service: RegistrationService = Depends(get_registration_service)
):
    """
    Initiate researcher registration.
    
    Flow:
    1. Validate registration data
    2. Store in pending_registrations table
    3. Send OTP via email
    4. Return success message
    """
    try:
        result = registration_service.initiate_researcher_registration(
            email=data.email,
            password=data.password,
            first_name=data.first_name,
            last_name=data.last_name,
            request=request
        )
        
        return InitiateRegistrationResponse(**result)
    
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
            detail="Registration initiation failed. Please try again."
        )


@router.post(
    "/organization/initiate",
    response_model=InitiateRegistrationResponse,
    status_code=status.HTTP_200_OK,
    summary="Initiate Organization Registration",
    description="Start organization registration - sends OTP to email"
)
async def initiate_organization_registration(
    data: InitiateRegistrationRequest,
    request: Request,
    registration_service: RegistrationService = Depends(get_registration_service)
):
    """
    Initiate organization registration.
    
    Flow:
    1. Validate registration data (including business email)
    2. Store in pending_registrations table
    3. Send OTP via email
    4. Return success message
    """
    try:
        result = registration_service.initiate_organization_registration(
            email=data.email,
            password=data.password,
            first_name=data.first_name,
            last_name=data.last_name,
            company_name=data.company_name,
            phone_number=data.phone_number,
            country=data.country,
            request=request
        )
        
        return InitiateRegistrationResponse(**result)
    
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
            detail="Registration initiation failed. Please try again."
        )


@router.post(
    "/verify-otp",
    response_model=VerifyOTPResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Verify Registration OTP",
    description="Verify OTP and complete user registration"
)
async def verify_registration_otp(
    data: VerifyOTPRequest,
    request: Request,
    registration_service: RegistrationService = Depends(get_registration_service)
):
    """
    Verify OTP and complete registration.
    
    Flow:
    1. Validate OTP
    2. Create user account from pending data
    3. Delete pending registration
    4. Return user data
    """
    try:
        result = registration_service.verify_registration_otp(
            email=data.email,
            otp=data.otp,
            request=request
        )
        
        return VerifyOTPResponse(**result)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Log error
        SecurityAudit.log_security_event(
            "OTP_VERIFICATION_ERROR",
            None,
            {"error": str(e), "email": data.email},
            request
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OTP verification failed. Please try again."
        )


@router.post(
    "/verify-token",
    response_model=VerifyTokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Verify Registration Token",
    description="Verify token (backup method) and complete user registration"
)
async def verify_registration_token(
    data: VerifyTokenRequest,
    request: Request,
    registration_service: RegistrationService = Depends(get_registration_service)
):
    """
    Verify token (backup method) and complete registration.
    
    This is the backup method when user clicks email link instead of entering OTP.
    """
    try:
        result = registration_service.verify_registration_token(
            token=data.token,
            request=request
        )
        
        return VerifyTokenResponse(**result)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Log error
        SecurityAudit.log_security_event(
            "TOKEN_VERIFICATION_ERROR",
            None,
            {"error": str(e), "token": data.token[:10] + "..."},
            request
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token verification failed. Please try again."
        )


@router.post(
    "/resend-otp",
    response_model=ResendOTPResponse,
    status_code=status.HTTP_200_OK,
    summary="Resend Registration OTP",
    description="Resend OTP for pending registration"
)
async def resend_registration_otp(
    data: ResendOTPRequest,
    request: Request,
    registration_service: RegistrationService = Depends(get_registration_service)
):
    """
    Resend OTP for pending registration.
    
    Use this when user didn't receive the OTP or it expired.
    """
    try:
        result = registration_service.resend_verification_otp(
            email=data.email,
            request=request
        )
        
        return ResendOTPResponse(**result)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Log error
        SecurityAudit.log_security_event(
            "RESEND_OTP_ERROR",
            None,
            {"error": str(e), "email": data.email},
            request
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to resend OTP. Please try again."
        )