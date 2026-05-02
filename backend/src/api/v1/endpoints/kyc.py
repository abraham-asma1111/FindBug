"""
KYC Endpoints — API routes for KYC verification (FREQ-01)
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Request
from sqlalchemy.orm import Session
from typing import Optional

from src.core.database import get_db
from src.core.security import SecurityAudit
from src.services.kyc_service import KYCService
from src.core.file_storage import FileStorageService
from src.domain.models.user import User
from src.core.dependencies import get_current_user, get_current_verified_user, require_financial
from src.core.exceptions import ConflictException
from src.api.v1.schemas.kyc import (
    KYCSubmissionRequest,
    KYCSubmissionResponse,
    KYCStatusResponse,
    KYCReviewRequest,
    KYCReviewResponse,
    KYCListResponse,
    KYCStatusUpdateRequest,
    KYCStatusUpdateResponse
)

router = APIRouter(prefix="/kyc", tags=["KYC Verification"])


def get_kyc_service(db: Session = Depends(get_db)) -> KYCService:
    """Dependency to get KYCService instance"""
    file_storage = FileStorageService(base_path="data/uploads/kyc")
    return KYCService(db, file_storage)


@router.post(
    "/submit",
    response_model=KYCSubmissionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit KYC Documents",
    description="Submit KYC verification documents (ID + selfie)"
)
async def submit_kyc(
    request: Request,
    document_type: str = Form(..., description="passport, national_id, drivers_license, residence_permit"),
    document_number: str = Form(..., description="Document identification number"),
    document_front: UploadFile = File(..., description="Front side of document"),
    document_back: Optional[UploadFile] = File(None, description="Back side of document (optional)"),
    selfie_photo: Optional[UploadFile] = File(None, description="Selfie photo (optional)"),
    current_user: User = Depends(get_current_verified_user),
    kyc_service: KYCService = Depends(get_kyc_service)
):
    """
    Submit KYC documents for verification.
    
    Requirements:
    - User must be email verified
    - Document type must be valid
    - Document front is required
    - Document back and selfie are optional
    
    Allowed document types:
    - passport
    - national_id
    - drivers_license
    - residence_permit
    """
    try:
        result = kyc_service.submit_kyc(
            user_id=str(current_user.id),
            document_type=document_type,
            document_number=document_number,
            document_front=document_front,
            document_back=document_back,
            selfie_photo=selfie_photo
        )
        
        # Log security event
        SecurityAudit.log_security_event(
            "KYC_SUBMITTED",
            str(current_user.id),
            {"kyc_id": result["kyc_id"], "document_type": document_type},
            request
        )
        
        return KYCSubmissionResponse(**result)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"KYC submission failed: {str(e)}"
        )


@router.get(
    "/status",
    response_model=KYCStatusResponse,
    summary="Get KYC Status",
    description="Get current KYC verification status"
)
async def get_kyc_status(
    current_user: User = Depends(get_current_user),
    kyc_service: KYCService = Depends(get_kyc_service)
):
    """
    Get KYC verification status for current user.
    
    Returns:
    - not_submitted: No KYC verification found
    - pending: KYC submitted, awaiting admin review
    - approved: KYC approved
    - rejected: KYC rejected
    - expired: KYC expired (needs renewal)
    """
    try:
        result = kyc_service.get_kyc_status(str(current_user.id))
        return KYCStatusResponse(**result)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get KYC status: {str(e)}"
        )


@router.get(
    "/admin/pending",
    response_model=KYCListResponse,
    summary="Get Pending KYC Verifications",
    description="Get list of pending KYC verifications for admin review (Admin only)"
)
async def get_pending_kyc(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(require_financial),
    kyc_service: KYCService = Depends(get_kyc_service)
):
    """
    Get pending KYC verifications (admin only).
    
    Returns list of KYC verifications awaiting review.
    """
    try:
        result = kyc_service.get_pending_kyc(skip=skip, limit=limit)
        return KYCListResponse(**result)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get pending KYC verifications: {str(e)}"
        )


@router.post(
    "/admin/review/{kyc_id}",
    response_model=KYCReviewResponse,
    summary="Review KYC Verification",
    description="Approve or reject KYC verification (Admin only)"
)
async def review_kyc(
    kyc_id: str,
    data: KYCReviewRequest,
    request: Request,
    current_user: User = Depends(require_financial),
    kyc_service: KYCService = Depends(get_kyc_service)
):
    """
    Admin review of KYC verification.
    
    Requirements:
    - User must be admin or staff
    - KYC must be in pending status
    - Rejection reason required if rejecting
    """
    try:
        result = kyc_service.review_kyc(
            kyc_id=kyc_id,
            reviewer_id=str(current_user.id),
            approved=data.approved,
            rejection_reason=data.rejection_reason
        )
        
        # Log security event
        SecurityAudit.log_security_event(
            "KYC_REVIEWED",
            str(current_user.id),
            {
                "kyc_id": kyc_id,
                "approved": data.approved,
                "user_id": result["user_id"]
            },
            request
        )
        
        return KYCReviewResponse(**result)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"KYC review failed: {str(e)}"
        )


@router.get(
    "/admin/history",
    response_model=KYCListResponse,
    summary="Get KYC History",
    description="Get KYC verification history (Admin only)"
)
async def get_kyc_history(
    user_id: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(require_financial),
    kyc_service: KYCService = Depends(get_kyc_service)
):
    """
    Get KYC verification history (admin only).
    
    Optional filters:
    - user_id: Filter by user
    - status: Filter by status (pending, approved, rejected, expired)
    """
    try:
        result = kyc_service.get_kyc_history(
            user_id=user_id,
            status=status,
            skip=skip,
            limit=limit
        )
        return KYCListResponse(**result)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get KYC history: {str(e)}"
        )


@router.put(
    "/admin/status/{kyc_id}",
    response_model=KYCStatusUpdateResponse,
    summary="Update KYC Status",
    description="Update KYC verification status (Admin only)"
)
async def update_kyc_status(
    kyc_id: str,
    data: KYCStatusUpdateRequest,
    request: Request,
    current_user: User = Depends(require_financial),
    kyc_service: KYCService = Depends(get_kyc_service)
):
    """
    Update KYC verification status (admin only).
    
    Allowed statuses:
    - pending
    - approved
    - rejected
    - expired
    """
    try:
        result = kyc_service.update_kyc_status(kyc_id=kyc_id, status=data.status)
        
        # Log security event
        SecurityAudit.log_security_event(
            "KYC_STATUS_UPDATED",
            str(current_user.id),
            {"kyc_id": kyc_id, "status": data.status},
            request
        )
        
        return KYCStatusUpdateResponse(**result)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"KYC status update failed: {str(e)}"
        )


@router.get(
    "/verifications",
    summary="Get KYC Verifications",
    description="Get KYC verifications list (Admin/Finance Officer only)"
)
async def get_kyc_verifications(
    status: Optional[str] = None,
    limit: int = 1000,
    current_user: User = Depends(require_financial),
    kyc_service: KYCService = Depends(get_kyc_service)
):
    """
    Get KYC verifications list (admin/finance officer only).
    
    Optional filters:
    - status: Filter by status (pending, approved, rejected)
    """
    try:
        from src.domain.models.kyc import KYCVerification
        from src.core.database import get_db
        
        db = next(get_db())
        query = db.query(KYCVerification)
        
        if status:
            query = query.filter(KYCVerification.status == status)
        
        verifications = query.order_by(KYCVerification.created_at.desc()).limit(limit).all()
        
        return {
            "verifications": [
                {
                    "id": str(v.id),
                    "user_id": str(v.user_id),
                    "user": {
                        "email": v.user.email if v.user else None,
                        "full_name": (
                            v.user.researcher.username if v.user and v.user.researcher and v.user.researcher.username else
                            v.user.organization.name if v.user and v.user.organization and v.user.organization.name else
                            v.user.staff.full_name if v.user and v.user.staff and v.user.staff.full_name else
                            v.user.email.split('@')[0] if v.user and v.user.email else "Unknown"
                        )
                    },
                    "email_verified": v.email_verified,
                    "persona_verified": v.persona_verified_at is not None,
                    "status": v.status,
                    "created_at": v.created_at.isoformat(),
                    "updated_at": v.updated_at.isoformat() if v.updated_at else None,
                    "verified_at": v.verified_at.isoformat() if v.verified_at else None,
                    "rejection_reason": v.rejection_reason
                }
                for v in verifications
            ],
            "total": len(verifications)
        }
    
    except Exception as e:
        from fastapi import status as http_status
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get KYC verifications: {str(e)}"
        )


@router.get(
    "/verifications/{kyc_id}",
    summary="Get KYC Verification Details",
    description="Get detailed KYC verification information (Admin/Finance Officer only)"
)
async def get_kyc_details(
    kyc_id: str,
    current_user: User = Depends(require_financial),
    kyc_service: KYCService = Depends(get_kyc_service)
):
    """Get detailed KYC verification information."""
    try:
        from src.domain.models.kyc import KYCVerification
        from src.core.database import get_db
        from uuid import UUID
        
        db = next(get_db())
        kyc = db.query(KYCVerification).filter(
            KYCVerification.id == UUID(kyc_id)
        ).first()
        
        if not kyc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="KYC verification not found"
            )
        
        return {
            "id": str(kyc.id),
            "user_id": str(kyc.user_id),
            "user_name": (
                kyc.user.researcher.username if kyc.user and kyc.user.researcher and kyc.user.researcher.username else
                kyc.user.organization.name if kyc.user and kyc.user.organization and kyc.user.organization.name else
                kyc.user.staff.full_name if kyc.user and kyc.user.staff and kyc.user.staff.full_name else
                kyc.user.email.split('@')[0] if kyc.user and kyc.user.email else "Unknown"
            ),
            "user_email": kyc.user.email if kyc.user else None,
            "document_type": kyc.document_type,
            "document_number": kyc.document_number,
            "document_front_url": kyc.document_front if kyc.document_front else None,
            "document_back_url": kyc.document_back if kyc.document_back else None,
            "selfie_photo_url": kyc.selfie_photo if kyc.selfie_photo else None,
            "status": kyc.status,
            "email_verified": kyc.email_verified,
            "persona_verified": kyc.persona_verified_at is not None,
            "submitted_at": kyc.created_at.isoformat(),
            "reviewed_at": kyc.verified_at.isoformat() if kyc.verified_at else None,
            "reviewed_by": str(kyc.verified_by) if kyc.verified_by else None,
            "rejection_reason": kyc.rejection_reason,
            "expires_at": kyc.expires_at.isoformat() if kyc.expires_at else None
        }
    
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid KYC ID format"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get KYC details: {str(e)}"
        )


@router.post(
    "/verifications/{kyc_id}/approve",
    summary="Approve KYC Verification",
    description="Approve KYC verification (Admin/Finance Officer only)"
)
async def approve_kyc_verification(
    kyc_id: str,
    request: Request,
    current_user: User = Depends(require_financial),
    kyc_service: KYCService = Depends(get_kyc_service)
):
    """Approve KYC verification."""
    try:
        result = kyc_service.review_kyc(
            kyc_id=kyc_id,
            reviewer_id=str(current_user.id),
            approved=True,
            rejection_reason=None
        )
        
        # Log security event
        SecurityAudit.log_security_event(
            "KYC_APPROVED",
            str(current_user.id),
            {"kyc_id": kyc_id},
            request
        )
        
        return {
            "message": "KYC verification approved",
            "kyc_id": kyc_id,
            "status": "approved"
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to approve KYC: {str(e)}"
        )


@router.post(
    "/verifications/{kyc_id}/reject",
    summary="Reject KYC Verification",
    description="Reject KYC verification (Admin/Finance Officer only)"
)
async def reject_kyc_verification(
    kyc_id: str,
    reason: str,
    request: Request,
    current_user: User = Depends(require_financial),
    kyc_service: KYCService = Depends(get_kyc_service)
):
    """Reject KYC verification."""
    try:
        result = kyc_service.review_kyc(
            kyc_id=kyc_id,
            reviewer_id=str(current_user.id),
            approved=False,
            rejection_reason=reason
        )
        
        # Log security event
        SecurityAudit.log_security_event(
            "KYC_REJECTED",
            str(current_user.id),
            {"kyc_id": kyc_id, "reason": reason},
            request
        )
        
        return {
            "message": "KYC verification rejected",
            "kyc_id": kyc_id,
            "status": "rejected"
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reject KYC: {str(e)}"
        )


# ============================================
# PERSONA KYC INTEGRATION ENDPOINTS
# ============================================

@router.post(
    "/persona/start",
    summary="Start Persona KYC Verification",
    description="Initialize Persona KYC verification flow"
)
async def start_persona_verification(
    request: Request,
    current_user: User = Depends(get_current_verified_user),
    kyc_service: KYCService = Depends(get_kyc_service)
):
    """
    Start Persona KYC verification.
    
    Returns inquiry_id and template_id for Persona SDK.
    """
    from src.core.logging import get_logger
    logger = get_logger(__name__)
    
    try:
        logger.info(f"Starting Persona verification for user {current_user.id}, role: {current_user.role}")
        
        result = await kyc_service.start_persona_verification(
            user_id=current_user.id,
            user_role=current_user.role
        )
        
        # Log security event
        SecurityAudit.log_security_event(
            "PERSONA_VERIFICATION_STARTED",
            str(current_user.id),
            {
                "inquiry_id": result["inquiry_id"],
                "user_role": current_user.role
            },
            request
        )
        
        return result
    
    except ValueError as e:
        logger.error(f"ValueError in start_persona_verification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Exception in start_persona_verification: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start Persona verification: {str(e)}"
        )


@router.get(
    "/persona/status",
    summary="Get Persona KYC Status",
    description="Get current Persona KYC verification status (ID verification only)"
)
async def get_persona_status(
    current_user: User = Depends(get_current_user),
    kyc_service: KYCService = Depends(get_kyc_service)
):
    """
    Get Persona KYC status for current user.
    
    IMPORTANT: This endpoint ONLY returns Persona ID verification status.
    Email verification is completely separate - use /kyc/email/status instead.
    
    Returns:
    - persona_status: created, pending, completed, failed
    - status: overall KYC status (approved, pending, rejected)
    """
    try:
        from src.domain.models.kyc import KYCVerification
        from src.core.database import get_db
        
        db = next(get_db())
        kyc = db.query(KYCVerification).filter(
            KYCVerification.user_id == current_user.id
        ).order_by(KYCVerification.created_at.desc()).first()
        
        if not kyc:
            return {
                "status": "not_started",
                "persona_status": None,
                "persona_inquiry_id": None
            }
        
        # ONLY return Persona-related data - NO email fields
        return {
            "status": kyc.status,
            "persona_status": kyc.persona_status,
            "persona_inquiry_id": kyc.persona_inquiry_id
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get Persona status: {str(e)}"
        )


@router.post(
    "/persona/webhook",
    summary="Persona Webhook Handler",
    description="Handle Persona webhook events"
)
async def persona_webhook(
    request: Request,
    kyc_service: KYCService = Depends(get_kyc_service)
):
    """
    Handle Persona webhook events.
    
    This endpoint is called by Persona when verification status changes.
    """
    try:
        # Get raw body for signature verification
        body = await request.body()
        signature = request.headers.get("Persona-Signature", "")
        
        # Parse JSON payload
        import json
        payload = json.loads(body)
        
        # Process webhook
        result = await kyc_service.handle_persona_webhook(payload, signature)
        
        return {"status": "success", "result": result}
    
    except Exception as e:
        # Log error but return 200 to prevent Persona retries
        from src.core.logging import get_logger
        logger = get_logger(__name__)
        logger.error(f"Persona webhook error: {str(e)}")
        
        return {"status": "error", "message": str(e)}


@router.post(
    "/persona/verify",
    summary="Verify Persona Inquiry",
    description="Verify Persona inquiry status after completion"
)
async def verify_persona_inquiry(
    inquiry_id: str,
    request: Request,
    current_user: User = Depends(get_current_verified_user),
    kyc_service: KYCService = Depends(get_kyc_service)
):
    """
    Verify Persona inquiry after user completes it.
    
    This is called by the frontend after Persona modal closes.
    """
    try:
        result = await kyc_service.verify_persona_inquiry(inquiry_id)
        
        # Log security event
        SecurityAudit.log_security_event(
            "PERSONA_INQUIRY_VERIFIED",
            str(current_user.id),
            {"inquiry_id": inquiry_id, "status": result.get("kyc_status")},
            request
        )
        
        return result
    
    except Exception as e:
        from src.core.logging import get_logger
        logger = get_logger(__name__)
        logger.error(f"Failed to verify inquiry: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify inquiry: {str(e)}"
        )


# ============================================
# EMAIL VERIFICATION ENDPOINTS (replaces SMS)
# ============================================

@router.post(
    "/email/send",
    summary="Send Email Verification Code",
    description="Send verification code to user's email (replaces SMS)"
)
async def send_email_verification(
    request: Request,
    current_user: User = Depends(get_current_verified_user),
    kyc_service: KYCService = Depends(get_kyc_service)
):
    """
    Send email verification code.
    
    Requirements:
    - Email address must be valid
    - Rate limited to 3 attempts per hour
    """
    # Get email from request body
    body = await request.json()
    email_address = body.get("email_address")
    
    if not email_address:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email address is required"
        )
    
    try:
        result = await kyc_service.send_email_verification(
            user_id=current_user.id,
            email_address=email_address
        )
        
        # Log security event (non-blocking)
        try:
            SecurityAudit.log_security_event(
                "EMAIL_VERIFICATION_SENT",
                str(current_user.id),
                {"email": result.get("email_address", email_address)},
                request
            )
        except Exception as log_error:
            # Don't fail the request if logging fails
            from src.core.logging import get_logger
            logger = get_logger(__name__)
            logger.warning(f"Failed to log security event: {log_error}")
        
        return result
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ConflictException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        # Log the full error for debugging
        from src.core.logging import get_logger
        logger = get_logger(__name__)
        logger.error(f"Error in send_email_verification: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send verification code: {str(e)}"
        )


@router.post(
    "/email/verify",
    summary="Verify Email Code",
    description="Verify code sent to user's email"
)
async def verify_email_code(
    request: Request,
    current_user: User = Depends(get_current_verified_user),
    kyc_service: KYCService = Depends(get_kyc_service)
):
    """
    Verify email code.
    
    Requirements:
    - Code must be valid and not expired
    """
    # Get code from request body
    body = await request.json()
    code = body.get("code")
    
    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification code is required"
        )
    
    try:
        result = await kyc_service.verify_email_code(
            user_id=current_user.id,
            code=code
        )
        
        # Log security event
        SecurityAudit.log_security_event(
            "EMAIL_VERIFIED",
            str(current_user.id),
            {"email": result["email_address"]},
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
            detail=f"Failed to verify email code: {str(e)}"
        )


@router.get(
    "/email/status",
    summary="Get Email Verification Status",
    description="Get email verification status for current user"
)
async def get_email_verification_status(
    current_user: User = Depends(get_current_user),
    kyc_service: KYCService = Depends(get_kyc_service)
):
    """
    Get email verification status.
    
    Returns:
    - email_verified: true/false (email verified status)
    - email_address: verified email address
    - can_verify_email: true/false (can verify email)
    """
    from src.core.logging import get_logger
    logger = get_logger(__name__)
    
    try:
        logger.info(f"Getting email status for user {current_user.id}")
        result = kyc_service.get_email_verification_status(current_user.id)
        logger.info(f"Email status result for user {current_user.id}: {result}")
        return result
    
    except Exception as e:
        logger.error(f"Error getting email status: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get email verification status: {str(e)}"
        )
