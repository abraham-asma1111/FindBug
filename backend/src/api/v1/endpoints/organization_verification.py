"""
Organization Verification Endpoints
Allows organizations to submit and check verification status
"""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.core.database import get_db
from src.api.v1.middlewares.auth import get_current_user, require_organization
from src.domain.models.user import User
from src.services.organization_verification_service import OrganizationVerificationService


router = APIRouter(prefix="/organization-verification", tags=["organization-verification"])


class VerificationSubmitRequest(BaseModel):
    """Request model for submitting verification."""
    business_license_url: Optional[str] = None
    tax_id: Optional[str] = None
    website: Optional[str] = None


@router.get("/status")
def get_verification_status(
    current_user: User = Depends(require_organization),
    db: Session = Depends(get_db)
):
    """
    Get current organization verification status.
    
    Returns verification status and details for the current organization.
    """
    service = OrganizationVerificationService(db)
    
    try:
        status_info = service.check_verification_status(
            organization_id=current_user.organization.id
        )
        
        return status_info
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/submit")
def submit_verification(
    verification_data: VerificationSubmitRequest,
    current_user: User = Depends(require_organization),
    db: Session = Depends(get_db)
):
    """
    Submit organization for verification.
    
    Organizations must provide business license and tax ID to be verified.
    """
    service = OrganizationVerificationService(db)
    
    try:
        org = service.submit_verification(
            organization_id=current_user.organization.id,
            business_license_url=verification_data.business_license_url,
            tax_id=verification_data.tax_id,
            website=verification_data.website
        )
        
        return {
            "message": "Verification submitted successfully. You'll be notified once the review is complete.",
            "organization_id": str(org.id),
            "verification_status": org.verification_status
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
