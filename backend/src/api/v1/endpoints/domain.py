"""
Domain Verification Endpoints for Organizations
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from urllib.parse import urlparse

from src.core.database import get_db
from src.core.security import SecurityAudit
from src.core.domain_verification import DomainVerificationService
from src.domain.models.user import User
from src.domain.models.program import BountyProgram, ProgramScope
from src.domain.models.scope_verification import ScopeVerification, VerificationStatus
from src.domain.repositories import OrganizationRepository
from src.core.dependencies import get_current_organization
from src.services.audit_service import AuditService
from src.services.scope_verification_service import ScopeVerificationService

router = APIRouter(prefix="/domain", tags=["Domain Verification"])


class StartDomainVerificationRequest(BaseModel):
    """Request to start domain verification"""
    domain: str
    method: str  # "dns", "file", or "email"


class VerifyDomainRequest(BaseModel):
    """Request to verify domain"""
    domain: str
    method: str


class PhaseOneVerificationRequest(BaseModel):
    """Phase 1: legal identity and liability attestation input."""
    business_license_url: str
    tax_id: str
    legal_name: str
    attest_owns_assets: bool
    attest_accepts_liability: bool


def _normalize_domain(domain: str) -> str:
    value = (domain or "").strip().lower()
    if value.startswith("http://") or value.startswith("https://"):
        value = urlparse(value).netloc
    if value.startswith("www."):
        value = value[4:]
    return value.strip(".")


def _website_domain(website: str | None) -> str | None:
    if not website:
        return None
    parsed = urlparse(website if website.startswith(("http://", "https://")) else f"https://{website}")
    host = parsed.netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    return host or None


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
    
    normalized_domain = _normalize_domain(data.domain)

    # Validate domain format
    is_valid, message = DomainVerificationService.validate_domain_format(normalized_domain)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )

    if DomainVerificationService.is_personal_email_domain(current_user.email or ""):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Corporate email is required for domain verification. "
                "Personal email providers are not allowed."
            ),
        )

    # Business rule: organization can verify only its own web domain (or subdomain)
    org_website_domain = _website_domain(organization.website)
    if org_website_domain:
        if normalized_domain != org_website_domain and not normalized_domain.endswith(f".{org_website_domain}"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Domain '{normalized_domain}' is outside your organization website domain "
                    f"'{org_website_domain}'. Update organization website first or verify a matching domain."
                ),
            )
    
    # Generate verification token
    verification_token = DomainVerificationService.generate_verification_token()
    
    # Store token in organization
    organization.domain_verification_token = verification_token
    organization.domain_verification_method = data.method
    organization.verification_status = "pending"
    db.commit()
    
    # Log security event
    SecurityAudit.log_security_event(
        "DOMAIN_VERIFICATION_STARTED",
        str(current_user.id),
        {"domain": normalized_domain, "method": data.method},
        request
    )
    
    # Return instructions based on method
    if data.method == "dns":
        return {
            "method": "dns",
            "domain": normalized_domain,
            "verification_token": verification_token,
            "instructions": f"Add the following TXT record to your DNS:\n\nName: {normalized_domain}\nType: TXT\nValue: findbug-verification={verification_token}\n\nAfter adding the record, click 'Verify Domain' to complete verification."
        }
    
    elif data.method == "file":
        return {
            "method": "file",
            "domain": normalized_domain,
            "verification_token": verification_token,
            "instructions": f"Upload a file to your website:\n\nURL: https://{normalized_domain}/.well-known/findbug-verification.txt\nContent: {verification_token}\n\nAfter uploading the file, click 'Verify Domain' to complete verification."
        }
    
    elif data.method == "email":
        admin_email = DomainVerificationService.generate_admin_email(data.domain)
        return {
            "method": "email",
            "domain": normalized_domain,
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
    
    normalized_domain = _normalize_domain(data.domain)
    verification_token = organization.domain_verification_token
    if organization.domain_verification_method and organization.domain_verification_method != data.method:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Verification method mismatch. Started with '{organization.domain_verification_method}', "
                f"but received '{data.method}'."
            ),
        )
    
    # Verify based on method
    if data.method == "dns":
        success, message = DomainVerificationService.verify_dns_txt_record(
            normalized_domain,
            verification_token
        )
    
    elif data.method == "file":
        success, message = await DomainVerificationService.verify_file_based(
            normalized_domain,
            verification_token
        )
    
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification method"
        )
    
    if success:
        # Organization remains unverified until explicit admin approval.
        # This endpoint only proves domain ownership technically.
        organization.domain_verified = False
        organization.verification_status = "pending_admin_review"
        
        # Add domain to verified_domains list
        if organization.verified_domains:
            domains = organization.verified_domains.split(',')
            if normalized_domain not in domains:
                domains.append(normalized_domain)
                organization.verified_domains = ','.join(domains)
        else:
            organization.verified_domains = normalized_domain
        
        # Clear verification token
        organization.domain_verification_token = None
        db.commit()
        
        # Log security event
        SecurityAudit.log_security_event(
            "DOMAIN_VERIFIED",
            str(current_user.id),
            {"domain": normalized_domain, "method": data.method},
            request
        )
        
        return {
            "success": True,
            "message": (
                f"{message}. Domain proof submitted and now awaiting admin approval."
            ),
            "domain": normalized_domain,
            "verified_domains": organization.verified_domains.split(',') if organization.verified_domains else [],
            "admin_approval_required": True,
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
        verified_domains = [d.strip() for d in organization.verified_domains.split(',') if d.strip()]

    # Reconcile legacy/inconsistent rows where the boolean is true but the list is empty.
    reconciled = False
    if organization.domain_verified and not verified_domains:
        fallback = _website_domain(organization.website)
        if fallback:
            verified_domains = [fallback]
            organization.verified_domains = fallback
            db.commit()
            reconciled = True
    
    return {
        "domain_verified": organization.domain_verified,
        "verified_domains": verified_domains,
        "verification_status": organization.verification_status,
        "phase1_submitted": bool(
            (organization.business_license_url or "").strip()
            and (organization.tax_id or "").strip()
        ),
        "admin_approval_required": organization.verification_status == "pending_admin_review",
        "reconciled_verified_domains": reconciled,
    }


@router.post(
    "/verify/phase1",
    response_model=dict,
    summary="Submit Phase 1 Legal Verification",
    description="Submit legal identity and liability attestations before domain ownership proof",
)
async def submit_phase_one_verification(
    data: PhaseOneVerificationRequest,
    request: Request,
    current_user: User = Depends(get_current_organization),
    db: Session = Depends(get_db),
):
    organization_repo = OrganizationRepository(db)
    organization = organization_repo.get_by_user_id(str(current_user.id))

    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    if not data.attest_owns_assets or not data.attest_accepts_liability:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Both legal attestations are required.",
        )

    if DomainVerificationService.is_personal_email_domain(current_user.email or ""):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Use a corporate email domain for organization verification.",
        )

    # Persist legal fields already available on organization profile
    organization.business_license_url = data.business_license_url.strip()
    organization.tax_id = data.tax_id.strip()
    organization.verification_status = "pending"
    db.commit()

    # Immutable-style append-only audit trail entry
    AuditService(db).log_action(
        action_type="organization_phase1_legal_submitted",
        action_category="security",
        target_type="organization",
        target_id=organization.id,
        actor_id=current_user.id,
        actor_role=current_user.role,
        actor_email=current_user.email,
        description="Organization submitted phase-1 legal verification and liability attestations",
        metadata={
            "legal_name": data.legal_name.strip(),
            "tax_id": data.tax_id.strip(),
            "business_license_url": data.business_license_url.strip(),
            "attest_owns_assets": data.attest_owns_assets,
            "attest_accepts_liability": data.attest_accepts_liability,
            "ip_address": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
        },
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        severity="warning",
    )

    return {
        "success": True,
        "message": "Phase 1 legal verification submitted and logged.",
        "organization_verification_status": organization.verification_status,
    }


@router.get(
    "/verify/phase3-summary",
    response_model=dict,
    summary="Phase 3 Scope Asset Validation Summary",
    description="Returns organization-level scope verification readiness for publish gating",
)
async def get_phase_three_summary(
    current_user: User = Depends(get_current_organization),
    db: Session = Depends(get_db),
):
    organization = OrganizationRepository(db).get_by_user_id(str(current_user.id))
    if not organization:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    programs = (
        db.query(BountyProgram)
        .filter(BountyProgram.organization_id == organization.id)
        .all()
    )

    verifiable_types = {"domain", "web_app", "api"}
    program_summaries = []
    total_verifiable = 0
    total_verified = 0

    for program in programs:
        scopes = db.query(ProgramScope).filter(ProgramScope.program_id == program.id).all()
        verifiable_scopes = [s for s in scopes if (s.asset_type or "").lower() in verifiable_types]
        verified_count = 0
        pending_assets = []

        for scope in verifiable_scopes:
            record = (
                db.query(ScopeVerification)
                .filter(ScopeVerification.scope_id == scope.id)
                .first()
            )
            scope_status = record.verification_status if record else VerificationStatus.UNVERIFIED.value
            if scope_status == VerificationStatus.VERIFIED.value:
                verified_count += 1
            else:
                pending_assets.append(
                    {
                        "scope_id": str(scope.id),
                        "asset_identifier": scope.asset_identifier,
                        "asset_type": scope.asset_type,
                        "verification_status": scope_status,
                    }
                )

        total_verifiable += len(verifiable_scopes)
        total_verified += verified_count

        program_summaries.append(
            {
                "program_id": str(program.id),
                "program_name": program.name,
                "program_status": program.status,
                "all_verified": len(verifiable_scopes) == verified_count,
                "verifiable_scope_count": len(verifiable_scopes),
                "verified_scope_count": verified_count,
                "pending_assets": pending_assets,
            }
        )

    return {
        "success": True,
        "total_programs": len(programs),
        "total_verifiable_scopes": total_verifiable,
        "total_verified_scopes": total_verified,
        "all_scopes_verified": total_verifiable > 0 and total_verifiable == total_verified,
        "programs": program_summaries,
    }


@router.post(
    "/verify/phase4/reverify-now",
    response_model=dict,
    summary="Phase 4 Ongoing Monitoring Reverification",
    description="Triggers reverification sweep for this organization's already-verified scopes",
)
async def run_phase_four_reverification(
    request: Request,
    current_user: User = Depends(get_current_organization),
    db: Session = Depends(get_db),
):
    organization = OrganizationRepository(db).get_by_user_id(str(current_user.id))
    if not organization:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    svc = ScopeVerificationService(db)
    results = svc.reverify_organization(organization.id)

    AuditService(db).log_action(
        action_type="organization_phase4_reverification_triggered",
        action_category="security",
        target_type="organization",
        target_id=organization.id,
        actor_id=current_user.id,
        actor_role=current_user.role,
        actor_email=current_user.email,
        description="Organization manually triggered phase-4 reverification sweep",
        metadata={
            "results": results,
            "ip_address": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
        },
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        severity="warning",
    )

    return {
        "success": True,
        "message": "Phase 4 reverification completed.",
        "results": results,
    }
