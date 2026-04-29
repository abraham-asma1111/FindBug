"""
SMS Phone Verification Endpoints
Step 2 of KYC process after Persona verification
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional

from src.core.database import get_db
from src.core.dependencies import get_current_user
from src.core.security import SecurityAudit
from src.services.kyc_service import KYCService
from src.domain.models.user import User
from src.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/kyc/sms", tags=["SMS Verification"])


class SendSMSRequest(BaseModel):
    """Request model for sending SMS verification code"""
    phone_number: str = Field(..., description="Phone number to verify (with country code)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "phone_number": "+251912345678"
            }
        }


class VerifySMSRequest(BaseModel):
    """Request model for verifying SMS code"""
    code: str = Field(..., min_length=6, max_length=6, description="6-digit verification code")
    
    class Config:
        json_schema_extra = {
            "example": {
                "code": "123456"
            }
        }


@router.post(
    "/send",
    summary="Send SMS Verification Code",
    description="Send SMS verification code to user's phone (Step 2 after Persona KYC)"
)
async def send_sms_verification(
    request_data: SendSMSRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send SMS verification code.
    
    Requirements:
    - Persona KYC must be approved first
    - Phone number must be valid
    - Rate limited to 3 attempts per hour
    """
    try:
        kyc_service = KYCService(db)
        
        result = await kyc_service.send_phone_verification(
            user_id=current_user.id,
            phone_number=request_data.phone_number
        )
        
        # Log security event
        SecurityAudit.log_security_event(
            "SMS_VERIFICATION_SENT",
            str(current_user.id),
            {
                "phone_number": result["phone_number"],
                "masked_phone": result["phone_number"][:7] + "****"
            },
            request
        )
        
        return result
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Log the technical error but return user-friendly message
        logger.error(f"Failed to send SMS verification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to send verification code. Please try again."
        )


@router.post(
    "/verify",
    summary="Verify SMS Code",
    description="Verify SMS code entered by user"
)
async def verify_sms_code(
    request_data: VerifySMSRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Verify SMS code.
    
    Requirements:
    - Code must match the one sent via SMS
    - Code must not be expired (10 minutes validity)
    """
    try:
        kyc_service = KYCService(db)
        
        result = await kyc_service.verify_phone_code(
            user_id=current_user.id,
            code=request_data.code
        )
        
        # Log security event
        SecurityAudit.log_security_event(
            "SMS_VERIFICATION_SUCCESS",
            str(current_user.id),
            {
                "phone_number": result["phone_number"],
                "verified_at": result["verified_at"]
            },
            request
        )
        
        return result
    
    except ValueError as e:
        # Log failed verification attempt
        SecurityAudit.log_security_event(
            "SMS_VERIFICATION_FAILED",
            str(current_user.id),
            {"reason": str(e)},
            request
        )
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Log the technical error but return user-friendly message
        logger.error(f"Failed to verify SMS code: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to verify code. Please try again."
        )


@router.get(
    "/status",
    summary="Get SMS Verification Status",
    description="Get current SMS verification status for user"
)
async def get_sms_verification_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get SMS verification status for current user."""
    try:
        kyc_service = KYCService(db)
        
        status_data = kyc_service.get_phone_verification_status(current_user.id)
        
        return status_data
    
    except Exception as e:
        # Log the technical error but return user-friendly message
        logger.error(f"Failed to get SMS verification status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to load verification status. Please refresh the page."
        )
