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
from src.core.dependencies import get_current_user, get_current_verified_user, require_admin
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
    current_user: User = Depends(require_admin),
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
    current_user: User = Depends(require_admin),
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
    current_user: User = Depends(require_admin),
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
    current_user: User = Depends(require_admin),
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
