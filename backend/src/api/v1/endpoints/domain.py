"""
Domain Verification Endpoints for Organizations
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.core.database import get_db
from src.core.security import SecurityAudit
from src.core.domain_verification import DomainVerificationService
from src.domain.models.user import User
from src.domain.repositories import OrganizationRepository
from src.api.v1.middlewares import get_current_organization

router = APIRouter(prefix="/domain", tags=["Domain Verification"])


class StartDomainVerificationRequest(BaseModel):
    """Request to start domain verification"""
    domain: str
    method: str  # "dns", "file", or "email"


class VerifyDomainRequest(BaseModel):
    """Request to verify domain"""
    domain: str
    method: str


@router.post(
    "/verify/start",
    response_model=dict,
    summary="Start Domain Verification",
    description="Start domain verification process for organization"
)
async def start_domain_verification(
    data: StartDomainVerificationRequest,
    request: Request,
    current_user: User = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    """
    Start domain verification process
    
    Methods:
    - dns: Add TXT record to DNS
    - file: Upload file to .well-known/
    - email: Receive code at admin@domain.com
    """
    organization_repo = OrganizationRepository(db)
    organization = organization_repo.get_by_user_id(str(current_user.id))
    
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    # Validate domain format
    is_valid, message = DomainVerificationService.validate_domain_format(data.domain)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    # Generate verification token
    verification_token = DomainVerificationService.generate_verification_token()
    
    # Store token in organization
    organization.domain_verification_token = verification_token
    db.commit()
    
    # Log security event
    SecurityAudit.log_event(
        user_id=str(current_user.id),
        event_type="domain_verification_started",
        ip_address=request.client.host,
        details={"domain": data.domain, "method": data.method}
    )
    
    # Return instructions based on method
    if data.method == "dns":
        return {
            "method": "dns",
            "domain": data.domain,
            "verification_token": verification_token,
            "instructions": f"Add the following TXT record to your DNS:\n\nName: {data.domain}\nType: TXT\nValue: findbug-verification={verification_token}\n\nAfter adding the record, click 'Verify Domain' to complete verification."
        }
    
    elif data.method == "file":
        return {
            "method": "file",
            "domain": data.domain,
            "verification_token": verification_token,
            "instructions": f"Upload a file to your website:\n\nURL: https://{data.domain}/.well-known/findbug-verification.txt\nContent: {verification_token}\n\nAfter uploading the file, click 'Verify Domain' to complete verification."
        }
    
    elif data.method == "email":
        admin_email = DomainVerificationService.generate_admin_email(data.domain)
        return {
            "method": "email",
            "domain": data.domain,
            "verification_token": verification_token,
            "instructions": f"A verification code will be sent to {admin_email}. Please check your email and enter the code to verify."
        }
    
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification method. Use: dns, file, or email"
        )


@router.post(
    "/verify/complete",
    response_model=dict,
    summary="Complete Domain Verification",
    description="Complete domain verification by checking DNS/file/email"
)
async def complete_domain_verification(
    data: VerifyDomainRequest,
    request: Request,
    current_user: User = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    """Complete domain verification"""
    organization_repo = OrganizationRepository(db)
    organization = organization_repo.get_by_user_id(str(current_user.id))
    
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    if not organization.domain_verification_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No verification in progress. Please start verification first."
        )
    
    verification_token = organization.domain_verification_token
    
    # Verify based on method
    if data.method == "dns":
        success, message = DomainVerificationService.verify_dns_txt_record(
            data.domain,
            verification_token
        )
    
    elif data.method == "file":
        success, message = await DomainVerificationService.verify_file_based(
            data.domain,
            verification_token
        )
    
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification method"
        )
    
    if success:
        # Update organization
        organization.domain_verified = True
        organization.verification_status = "verified"
        
        # Add domain to verified_domains list
        if organization.verified_domains:
            domains = organization.verified_domains.split(',')
            if data.domain not in domains:
                domains.append(data.domain)
                organization.verified_domains = ','.join(domains)
        else:
            organization.verified_domains = data.domain
        
        # Clear verification token
        organization.domain_verification_token = None
        db.commit()
        
        # Log security event
        SecurityAudit.log_event(
            user_id=str(current_user.id),
            event_type="domain_verified",
            ip_address=request.client.host,
            details={"domain": data.domain, "method": data.method}
        )
        
        return {
            "success": True,
            "message": message,
            "domain": data.domain,
            "verified_domains": organization.verified_domains.split(',') if organization.verified_domains else []
        }
    
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )


@router.get(
    "/verified",
    response_model=dict,
    summary="Get Verified Domains",
    description="Get list of verified domains for organization"
)
async def get_verified_domains(
    current_user: User = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    """Get verified domains"""
    organization_repo = OrganizationRepository(db)
    organization = organization_repo.get_by_user_id(str(current_user.id))
    
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    verified_domains = []
    if organization.verified_domains:
        verified_domains = organization.verified_domains.split(',')
    
    return {
        "domain_verified": organization.domain_verified,
        "verified_domains": verified_domains,
        "verification_status": organization.verification_status
    }
