"""
Organization Verification Endpoints
Organizations submit identity & asset ownership evidence for manual Admin review.
No automated DNS pinging — all verification is done manually by Admin.
"""
import json
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.core.database import get_db
from src.api.v1.middlewares.auth import get_current_user, require_organization
from src.domain.models.user import User
from src.domain.models.organization import Organization


router = APIRouter(prefix="/organization-verification", tags=["organization-verification"])


class VerificationSubmitRequest(BaseModel):
    """
    Full evidence package an organization submits for manual Admin review.
    Admin will inspect all of these fields and decide to approve or reject.
    """
    # Identity
    legal_name: Optional[str] = None           # Official registered legal entity name
    corporate_email: Optional[str] = None       # e.g. admin@company.com
    phone_number: Optional[str] = None
    tax_id: Optional[str] = None               # EIN / VAT / Tax ID
    business_license_url: Optional[str] = None  # URL to uploaded license doc

    # Asset ownership
    website: Optional[str] = None
    owned_domains: Optional[List[str]] = None    # Root domains the org claims to own
    owned_subdomains: Optional[List[str]] = None # Subdomains / assets

    # DNS evidence (text entered by org — NOT pinged automatically)
    dns_txt_record: Optional[str] = None        # The TXT record they say they've added

    # Additional context
    additional_notes: Optional[str] = None      # Free-text: explain ownership, context, etc.


@router.get("/status")
def get_verification_status(
    current_user: User = Depends(require_organization),
    db: Session = Depends(get_db)
):
    """
    Get current organization verification status.
    """
    org = db.query(Organization).filter(
        Organization.user_id == current_user.id
    ).first()

    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    return {
        "organization_id": str(org.id),
        "company_name": org.company_name,
        "verification_status": org.verification_status,
        "legal_name": org.legal_name,
        "corporate_email": org.corporate_email,
        "phone_number": org.phone_number,
        "tax_id": org.tax_id,
        "business_license_url": org.business_license_url,
        "website": org.website,
        "owned_domains": json.loads(org.owned_domains) if org.owned_domains else [],
        "owned_subdomains": json.loads(org.owned_subdomains) if org.owned_subdomains else [],
        "dns_txt_record": org.domain_verification_token,
        "additional_notes": org.additional_notes,
        "can_create_programs": org.verification_status == "active",
        "submitted_for_review": org.verification_status in ["submitted", "active", "rejected"],
    }


@router.post("/submit")
def submit_verification(
    data: VerificationSubmitRequest,
    current_user: User = Depends(require_organization),
    db: Session = Depends(get_db)
):
    """
    Submit identity & domain ownership evidence for manual Admin review.
    No automated checks are performed — Admin reviews all fields manually.
    """
    org = db.query(Organization).filter(
        Organization.user_id == current_user.id
    ).first()

    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    # Store all evidence fields
    if data.legal_name:
        org.legal_name = data.legal_name
    if data.corporate_email:
        org.corporate_email = data.corporate_email
    if data.phone_number:
        org.phone_number = data.phone_number
    if data.tax_id:
        org.tax_id = data.tax_id
    if data.business_license_url:
        org.business_license_url = data.business_license_url
    if data.website:
        org.website = data.website
    if data.owned_domains is not None:
        org.owned_domains = json.dumps(data.owned_domains)
    if data.owned_subdomains is not None:
        org.owned_subdomains = json.dumps(data.owned_subdomains)
    if data.dns_txt_record:
        org.domain_verification_token = data.dns_txt_record
    if data.additional_notes:
        org.additional_notes = data.additional_notes

    # Set status to submitted for Admin queue
    org.verification_status = "submitted"

    db.commit()
    db.refresh(org)

    return {
        "message": "Verification evidence submitted successfully. An admin will review your submission and activate your account. This process typically takes 1–2 business days.",
        "organization_id": str(org.id),
        "verification_status": org.verification_status,
    }
