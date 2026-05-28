"""Scope Verification API Endpoints.

Routes:
    POST /scopes/{scope_id}/verification/initiate
    POST /scopes/{scope_id}/verification/check
    GET  /scopes/{scope_id}/verification
    POST /scopes/{scope_id}/verification/regenerate
    POST /scopes/{scope_id}/verification/admin/approve
    POST /scopes/{scope_id}/verification/admin/revoke
    POST /scopes/{scope_id}/verification/admin/suspend
    GET  /programs/{program_id}/verification-status
"""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from pydantic import BaseModel, validator
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.api.v1.middlewares.auth import get_current_user, require_organization
from src.domain.models.user import User
from src.domain.models.scope_verification import VerificationMethod
from src.services.scope_verification_service import ScopeVerificationService

router = APIRouter(tags=["Scope Verification"])


# ── Request/Response schemas ──────────────────────────────────────────────────

class InitiateRequest(BaseModel):
    method: str  # dns_txt | file_based

    @validator("method")
    def validate_method(cls, v):
        valid = {VerificationMethod.DNS_TXT.value, VerificationMethod.FILE_BASED.value}
        if v not in valid:
            raise ValueError(f"method must be one of: {valid}")
        return v


class RegenerateRequest(BaseModel):
    method: str = VerificationMethod.DNS_TXT.value

    @validator("method")
    def validate_method(cls, v):
        valid = {VerificationMethod.DNS_TXT.value, VerificationMethod.FILE_BASED.value}
        if v not in valid:
            raise ValueError(f"method must be one of: {valid}")
        return v


class AdminActionRequest(BaseModel):
    note: Optional[str] = None


def _verification_response(record) -> dict:
    """Serialize a ScopeVerification record to a clean API response."""
    return {
        "id":                   str(record.id),
        "scope_id":             str(record.scope_id),
        "domain":               record.domain,
        "root_domain":          record.root_domain,
        "verification_method":  record.verification_method,
        "verification_status":  record.verification_status,
        "verification_token":   record.verification_token,
        "verified_at":          record.verified_at.isoformat() if record.verified_at else None,
        "expires_at":           record.expires_at.isoformat() if record.expires_at else None,
        "last_checked":         record.last_checked.isoformat() if record.last_checked else None,
        "attempt_count":        record.attempt_count,
        "failure_reason":       record.failure_reason,
        "admin_note":           record.admin_note,
        "created_at":           record.created_at.isoformat() if record.created_at else None,
        "updated_at":           record.updated_at.isoformat() if record.updated_at else None,
        # Derived helpers for the UI
        "dns_record_name":      record.dns_record_name,
        "dns_record_value":     record.dns_record_value,
        "file_verification_url": record.file_verification_url,
    }


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post(
    "/scopes/{scope_id}/verification/initiate",
    summary="Initiate scope domain verification",
)
def initiate_verification(
    scope_id: UUID,
    body: InitiateRequest,
    request: Request,
    current_user: User = Depends(require_organization),
    db: Session = Depends(get_db),
):
    """
    Generate a verification token for a scope and return instructions.

    - **dns_txt**: Add TXT record `ptaas-verification=<token>` to your DNS.
    - **file_based**: Host `<token>` at `https://<domain>/.well-known/ptaas-verification.txt`.
    """
    svc = ScopeVerificationService(db)
    record = svc.initiate_verification(
        scope_id=scope_id,
        method=body.method,
        actor_id=current_user.id,
        actor_email=current_user.email,
        ip_address=request.client.host if request.client else None,
    )
    return {
        **_verification_response(record),
        "instructions": _build_instructions(record),
    }


@router.post(
    "/scopes/{scope_id}/verification/check",
    summary="Run the verification check",
)
def check_verification(
    scope_id: UUID,
    request: Request,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(require_organization),
    db: Session = Depends(get_db),
):
    """
    Trigger DNS/file check for the scope.  Updates status to VERIFIED or FAILED.
    The check runs synchronously and returns the updated state immediately.
    """
    svc = ScopeVerificationService(db)
    record = svc.check_verification(
        scope_id=scope_id,
        actor_id=current_user.id,
        actor_email=current_user.email,
        ip_address=request.client.host if request.client else None,
    )
    return {
        **_verification_response(record),
        "message": "Domain verification data submitted to Admin for manual review."
    }


@router.get(
    "/scopes/{scope_id}/verification",
    summary="Get current verification state",
)
def get_verification(
    scope_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return the current verification record for a scope, or 404 if not initiated."""
    svc = ScopeVerificationService(db)
    record = svc.get_scope_verification(scope_id)
    if not record:
        return {
            "scope_id": str(scope_id),
            "verification_status": "unverified",
            "message": "Verification not yet initiated.",
        }
    return _verification_response(record)


@router.post(
    "/scopes/{scope_id}/verification/regenerate",
    summary="Regenerate verification token",
)
def regenerate_token(
    scope_id: UUID,
    body: RegenerateRequest,
    request: Request,
    current_user: User = Depends(require_organization),
    db: Session = Depends(get_db),
):
    """Rotate the verification token and reset TTL. Resets status to PENDING."""
    svc = ScopeVerificationService(db)
    record = svc.regenerate_token(
        scope_id=scope_id,
        method=body.method,
        actor_id=current_user.id,
        actor_email=current_user.email,
        ip_address=request.client.host if request.client else None,
    )
    return {
        **_verification_response(record),
        "instructions": _build_instructions(record),
    }


# ── Program-level summary ─────────────────────────────────────────────────────

@router.get(
    "/programs/{program_id}/verification-status",
    summary="Get verification status for all scopes in a program",
)
def program_verification_status(
    program_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Returns a per-scope verification summary and whether the program
    is publishable (all verifiable scopes are VERIFIED).
    """
    svc = ScopeVerificationService(db)
    return svc.get_program_verification_summary(program_id)


# ── Admin endpoints ───────────────────────────────────────────────────────────

def _require_admin(current_user: User):
    if current_user.role not in ("admin", "super_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required.",
        )


@router.post(
    "/scopes/{scope_id}/verification/admin/approve",
    summary="[Admin] Manually approve scope verification",
)
def admin_approve(
    scope_id: UUID,
    body: AdminActionRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Admin bypass: mark scope as VERIFIED without DNS/file check."""
    _require_admin(current_user)
    svc = ScopeVerificationService(db)
    record = svc.admin_approve(
        scope_id=scope_id,
        admin_id=current_user.id,
        admin_email=current_user.email,
        note=body.note,
        ip_address=request.client.host if request.client else None,
    )
    return _verification_response(record)


@router.post(
    "/scopes/{scope_id}/verification/admin/revoke",
    summary="[Admin] Revoke scope verification",
)
def admin_revoke(
    scope_id: UUID,
    body: AdminActionRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Admin: revoke a VERIFIED scope back to UNVERIFIED."""
    _require_admin(current_user)
    svc = ScopeVerificationService(db)
    record = svc.admin_revoke(
        scope_id=scope_id,
        admin_id=current_user.id,
        admin_email=current_user.email,
        note=body.note,
        ip_address=request.client.host if request.client else None,
    )
    return _verification_response(record)


@router.post(
    "/scopes/{scope_id}/verification/admin/suspend",
    summary="[Admin] Suspend scope verification",
)
def admin_suspend(
    scope_id: UUID,
    body: AdminActionRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Admin: suspend a scope (e.g. ownership in dispute)."""
    _require_admin(current_user)
    svc = ScopeVerificationService(db)
    record = svc.admin_suspend(
        scope_id=scope_id,
        admin_id=current_user.id,
        admin_email=current_user.email,
        note=body.note,
        ip_address=request.client.host if request.client else None,
    )
    return _verification_response(record)


# ── Admin: trigger reverification sweep ───────────────────────────────────────

@router.post(
    "/admin/verification/reverify-all",
    summary="[Admin] Trigger reverification sweep of all VERIFIED scopes",
)
def trigger_reverification(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Manually trigger the reverification sweep (normally runs daily via scheduler)."""
    _require_admin(current_user)
    svc = ScopeVerificationService(db)
    results = svc.reverify_all()
    return {"message": "Reverification sweep complete.", "results": results}


# ── Instruction builder ───────────────────────────────────────────────────────

def _build_instructions(record) -> dict:
    if record.verification_method == "dns_txt":
        return {
            "method": "DNS TXT Record",
            "steps": [
                f"Log in to your DNS provider for '{record.root_domain}'.",
                "Add a new TXT record:",
                f"  Host/Name: {record.dns_record_name}",
                f"  Type: TXT",
                f"  Value: {record.dns_record_value}",
                f"  TTL: 300 (5 minutes)",
                "DNS changes can take up to 24–48 hours to propagate globally.",
                "Click 'Run Verification' once the record is live.",
            ],
            "record_name":  record.dns_record_name,
            "record_type":  "TXT",
            "record_value": record.dns_record_value,
            "expires_in":   "48 hours",
        }
    else:
        return {
            "method": "File-Based Verification",
            "steps": [
                f"Create the file at the following URL on your server:",
                f"  URL: {record.file_verification_url}",
                f"  Content: {record.verification_token}",
                "The file must:",
                "  • Be accessible via HTTPS (not HTTP)",
                "  • Return HTTP 200",
                "  • Contain ONLY the token (no extra whitespace or lines)",
                "Click 'Run Verification' once the file is live.",
            ],
            "file_url":   record.file_verification_url,
            "file_content": record.verification_token,
            "expires_in": "48 hours",
        }
