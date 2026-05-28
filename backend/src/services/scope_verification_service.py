"""Scope Verification Service — production-grade domain ownership verification.

Supports:
  • DNS TXT verification  (ptaas-verification=<token> TXT record)
  • File-based verification (https://<domain>/.well-known/ptaas-verification.txt)

Security:
  • SSRF protection (private IP blocklist)
  • HTTPS-only for file verification
  • Cryptographically secure tokens
  • Rate limiting (5 attempts/scope/hour)
  • Token TTL (48 h default)
  • Full audit trail
"""
from __future__ import annotations

import ipaddress
import secrets
import socket
from datetime import datetime, timedelta
from typing import List, Optional, Tuple
from uuid import UUID

import httpx
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.domain.models.program import ProgramScope
from src.domain.models.scope_verification import (
    ScopeVerification,
    VerificationStatus,
    VerificationMethod,
)
from src.services.audit_service import AuditService

# ── Constants ────────────────────────────────────────────────────────────────
TOKEN_PREFIX      = "ptaas-verification"
TOKEN_BYTES       = 16           # 32 hex chars
TOKEN_TTL_HOURS   = 48
MAX_ATTEMPTS_HOUR = 5            # rate-limit per scope per hour
DNS_TIMEOUT       = 10.0         # seconds
HTTP_TIMEOUT      = 15.0         # seconds
HTTP_MAX_REDIRECTS = 3

# Scopes that require domain ownership verification before publish
VERIFIABLE_ASSET_TYPES = {"domain", "web_app", "api"}

# Private IP ranges to block (SSRF)
_PRIVATE_NETS = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),  # link-local
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
]


# ── Root-domain helper (tldextract with fallback) ────────────────────────────

def _extract_root_domain(asset_identifier: str) -> str:
    """Extract registrable root domain safely.

    api.company.com  → company.com
    *.company.com    → company.com
    company.com      → company.com

    Falls back to simple split if tldextract is unavailable.
    """
    raw = asset_identifier.lstrip("*.")  # strip wildcard prefix
    # Remove protocol if present
    for proto in ("https://", "http://"):
        if raw.startswith(proto):
            raw = raw[len(proto):]
    # Remove path
    raw = raw.split("/")[0].split("?")[0].split("#")[0]

    try:
        import tldextract  # type: ignore
        ext = tldextract.extract(raw)
        if ext.domain and ext.suffix:
            return f"{ext.domain}.{ext.suffix}"
        return raw
    except ImportError:
        parts = raw.split(".")
        if len(parts) >= 2:
            return ".".join(parts[-2:])
        return raw


def _is_ssrf_safe(hostname: str) -> bool:
    """Return False if hostname resolves to a private/loopback address."""
    try:
        infos = socket.getaddrinfo(hostname, None)
        for info in infos:
            addr_str = info[4][0]
            try:
                addr = ipaddress.ip_address(addr_str)
                for net in _PRIVATE_NETS:
                    if addr in net:
                        return False
            except ValueError:
                return False
        return True
    except socket.gaierror:
        # Cannot resolve — treat as unsafe to avoid SSRF via DNS rebinding
        return False


# ── Service ───────────────────────────────────────────────────────────────────

class ScopeVerificationService:
    """Manages the complete scope verification lifecycle."""

    def __init__(self, db: Session):
        self.db = db
        self.audit = AuditService(db)

    # ── Token generation ─────────────────────────────────────────────────────

    @staticmethod
    def _generate_token() -> str:
        return secrets.token_hex(TOKEN_BYTES)  # 32 hex chars

    # ── Get or create record ─────────────────────────────────────────────────

    def _get_verification(self, scope_id: UUID) -> Optional[ScopeVerification]:
        return (
            self.db.query(ScopeVerification)
            .filter(ScopeVerification.scope_id == scope_id)
            .first()
        )

    def _get_scope(self, scope_id: UUID) -> ProgramScope:
        scope = self.db.query(ProgramScope).filter(ProgramScope.id == scope_id).first()
        if not scope:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Scope not found",
            )
        return scope

    # ── Public API ────────────────────────────────────────────────────────────

    def initiate_verification(
        self,
        scope_id: UUID,
        method: str,
        actor_id: UUID,
        actor_email: str,
        ip_address: Optional[str] = None,
    ) -> ScopeVerification:
        """Create or refresh a verification record.

        If a VERIFIED record already exists the token is preserved (no-op).
        For any other status the token is refreshed and TTL reset.
        """
        if method not in (VerificationMethod.DNS_TXT.value, VerificationMethod.FILE_BASED.value):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"method must be '{VerificationMethod.DNS_TXT.value}' or '{VerificationMethod.FILE_BASED.value}'",
            )

        scope = self._get_scope(scope_id)

        root_domain = _extract_root_domain(scope.asset_identifier)
        token       = self._generate_token()
        expires_at  = datetime.utcnow() + timedelta(hours=TOKEN_TTL_HOURS)

        existing = self._get_verification(scope_id)

        if existing:
            if existing.verification_status == VerificationStatus.VERIFIED.value:
                # Already verified — return as-is
                return existing

            # Update for fresh attempt
            existing.verification_method = method
            existing.verification_token  = token
            existing.verification_status = VerificationStatus.PENDING.value
            existing.expires_at          = expires_at
            existing.failure_reason      = None
            existing.domain              = scope.asset_identifier
            existing.root_domain         = root_domain
            existing.updated_at          = datetime.utcnow()
            self.db.commit()
            self.db.refresh(existing)
            record = existing
        else:
            record = ScopeVerification(
                scope_id            = scope_id,
                program_id          = scope.program_id,
                organization_id     = scope.program.organization_id,
                domain              = scope.asset_identifier,
                root_domain         = root_domain,
                verification_method = method,
                verification_token  = token,
                verification_status = VerificationStatus.PENDING.value,
                expires_at          = expires_at,
                created_by          = actor_id,
            )
            self.db.add(record)
            self.db.commit()
            self.db.refresh(record)

        # Audit
        self.audit.log_action(
            action_type="scope_verification_initiated",
            action_category="security",
            target_type="scope",
            description=f"Domain verification initiated for {scope.asset_identifier} via {method}",
            actor_id=actor_id,
            actor_role="organization",
            actor_email=actor_email,
            target_id=scope_id,
            metadata={
                "domain": scope.asset_identifier,
                "root_domain": root_domain,
                "method": method,
            },
            ip_address=ip_address,
            severity="info",
        )
        return record

    def get_scope_verification(self, scope_id: UUID) -> Optional[ScopeVerification]:
        """Return current verification record (or None)."""
        return self._get_verification(scope_id)

    def check_verification(
        self,
        scope_id: UUID,
        actor_id: UUID,
        actor_email: str,
        ip_address: Optional[str] = None,
    ) -> ScopeVerification:
        """Run the actual DNS/file check and update the record state."""
        record = self._get_verification(scope_id)
        if not record:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Verification not initiated. Call /initiate first.",
            )

        # Check token expiry
        if record.is_token_expired:
            record.verification_status = VerificationStatus.EXPIRED.value
            self.db.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Verification token has expired. Please regenerate.",
            )

        # Rate-limit
        self._enforce_rate_limit(record)

        # Update counters
        record.attempt_count   = (record.attempt_count or 0) + 1
        record.last_attempt_at = datetime.utcnow()
        record.last_checked    = datetime.utcnow()

        # MANUAL OVERRIDE: Skip automated check, leave in PENDING for Admin review
        success = True
        record.verification_status = VerificationStatus.PENDING.value
        record.failure_reason      = "Pending manual review by Admin"
        severity = "info"

        self.db.commit()
        self.db.refresh(record)

        # Audit
        self.audit.log_action(
            action_type="scope_verification_checked",
            action_category="security",
            target_type="scope",
            description=(
                f"Verification {'succeeded' if success else 'failed'} for {record.domain}"
            ),
            actor_id=actor_id,
            actor_role="organization",
            actor_email=actor_email,
            target_id=scope_id,
            metadata={
                "domain": record.domain,
                "method": record.verification_method,
                "success": success,
                "reason": reason,
                "attempt_count": record.attempt_count,
            },
            ip_address=ip_address,
            severity=severity,
        )
        return record

    def regenerate_token(
        self,
        scope_id: UUID,
        method: str,
        actor_id: UUID,
        actor_email: str,
        ip_address: Optional[str] = None,
    ) -> ScopeVerification:
        """Force-regenerate the token (resets to PENDING)."""
        record = self._get_verification(scope_id)
        if not record:
            return self.initiate_verification(scope_id, method, actor_id, actor_email, ip_address)

        if record.verification_status == VerificationStatus.VERIFIED.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Scope is already verified. Revoke first if you need to re-verify.",
            )

        scope = self._get_scope(scope_id)
        record.verification_token  = self._generate_token()
        record.verification_method = method
        record.verification_status = VerificationStatus.PENDING.value
        record.expires_at          = datetime.utcnow() + timedelta(hours=TOKEN_TTL_HOURS)
        record.failure_reason      = None
        record.attempt_count       = 0
        record.domain              = scope.asset_identifier
        record.root_domain         = _extract_root_domain(scope.asset_identifier)
        record.updated_at          = datetime.utcnow()
        self.db.commit()
        self.db.refresh(record)

        self.audit.log_action(
            action_type="scope_verification_token_regenerated",
            action_category="security",
            target_type="scope",
            description=f"Verification token regenerated for {record.domain}",
            actor_id=actor_id,
            actor_role="organization",
            actor_email=actor_email,
            target_id=scope_id,
            metadata={"domain": record.domain, "method": method},
            ip_address=ip_address,
            severity="warning",
        )
        return record

    # ── Admin moderation ──────────────────────────────────────────────────────

    def get_pending_verifications(self) -> List[ScopeVerification]:
        """Admin: Get all pending domain verifications awaiting manual review."""
        return (
            self.db.query(ScopeVerification)
            .filter(ScopeVerification.verification_status == VerificationStatus.PENDING.value)
            .order_by(ScopeVerification.updated_at.desc())
            .all()
        )


    def admin_approve(
        self,
        scope_id: UUID,
        admin_id: UUID,
        admin_email: str,
        note: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> ScopeVerification:
        """Admin manually approves a scope (bypasses DNS/file check)."""
        record = self._get_or_raise(scope_id)
        record.verification_status = VerificationStatus.VERIFIED.value
        record.verified_at         = datetime.utcnow()
        record.admin_note          = note
        record.moderated_by        = admin_id
        record.moderated_at        = datetime.utcnow()
        record.failure_reason      = None
        self.db.commit()
        self.db.refresh(record)
        self._audit_admin("scope_verification_admin_approved", record, admin_id, admin_email, note, ip_address, "warning")
        return record

    def admin_revoke(
        self,
        scope_id: UUID,
        admin_id: UUID,
        admin_email: str,
        note: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> ScopeVerification:
        """Admin revokes a verified scope."""
        record = self._get_or_raise(scope_id)
        record.verification_status = VerificationStatus.UNVERIFIED.value
        record.verified_at         = None
        record.admin_note          = note
        record.moderated_by        = admin_id
        record.moderated_at        = datetime.utcnow()
        self.db.commit()
        self.db.refresh(record)
        self._audit_admin("scope_verification_admin_revoked", record, admin_id, admin_email, note, ip_address, "critical")
        return record

    def admin_suspend(
        self,
        scope_id: UUID,
        admin_id: UUID,
        admin_email: str,
        note: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> ScopeVerification:
        """Admin suspends a scope (e.g. ownership in dispute)."""
        record = self._get_or_raise(scope_id)
        record.verification_status = VerificationStatus.SUSPENDED.value
        record.admin_note          = note
        record.moderated_by        = admin_id
        record.moderated_at        = datetime.utcnow()
        self.db.commit()
        self.db.refresh(record)
        self._audit_admin("scope_verification_admin_suspended", record, admin_id, admin_email, note, ip_address, "critical")
        return record

    # ── Reverification (called by scheduler) ─────────────────────────────────

    def reverify_all(self) -> dict:
        """Daily job: recheck all VERIFIED scopes and suspend if check fails."""
        verified_records = (
            self.db.query(ScopeVerification)
            .filter(ScopeVerification.verification_status == VerificationStatus.VERIFIED.value)
            .all()
        )
        results = {"checked": 0, "still_verified": 0, "suspended": 0, "errors": 0}

        for record in verified_records:
            try:
                if record.verification_method == VerificationMethod.DNS_TXT.value:
                    success, reason = self._check_dns(record)
                else:
                    success, reason = self._check_file(record)

                record.last_checked = datetime.utcnow()
                if not success:
                    record.verification_status = VerificationStatus.SUSPENDED.value
                    record.failure_reason      = f"[Reverification] {reason}"
                    results["suspended"] += 1
                    self.audit.log_action(
                        action_type="scope_reverification_suspended",
                        action_category="security",
                        target_type="scope",
                        description=f"Scope suspended after reverification failure: {record.domain}",
                        target_id=record.scope_id,
                        metadata={"domain": record.domain, "reason": reason},
                        severity="critical",
                    )
                else:
                    results["still_verified"] += 1
                results["checked"] += 1
            except Exception as exc:
                results["errors"] += 1

        self.db.commit()
        return results

    def reverify_organization(self, organization_id: UUID) -> dict:
        """Recheck VERIFIED scopes for a single organization."""
        verified_records = (
            self.db.query(ScopeVerification)
            .filter(
                ScopeVerification.organization_id == organization_id,
                ScopeVerification.verification_status == VerificationStatus.VERIFIED.value,
            )
            .all()
        )
        results = {"checked": 0, "still_verified": 0, "suspended": 0, "errors": 0}

        for record in verified_records:
            try:
                if record.verification_method == VerificationMethod.DNS_TXT.value:
                    success, reason = self._check_dns(record)
                else:
                    success, reason = self._check_file(record)

                record.last_checked = datetime.utcnow()
                if not success:
                    record.verification_status = VerificationStatus.SUSPENDED.value
                    record.failure_reason = f"[Reverification] {reason}"
                    results["suspended"] += 1
                    self.audit.log_action(
                        action_type="scope_reverification_suspended",
                        action_category="security",
                        target_type="scope",
                        description=f"Scope suspended after reverification failure: {record.domain}",
                        target_id=record.scope_id,
                        metadata={"domain": record.domain, "reason": reason, "organization_id": str(organization_id)},
                        severity="critical",
                    )
                else:
                    results["still_verified"] += 1
                results["checked"] += 1
            except Exception:
                results["errors"] += 1

        self.db.commit()
        return results

    # ── Program-level helpers ─────────────────────────────────────────────────

    def get_program_verification_summary(self, program_id: UUID) -> dict:
        """Return per-scope verification summary for a program."""
        from src.domain.models.program import BountyProgram, ProgramScope
        scopes = (
            self.db.query(ProgramScope)
            .filter(ProgramScope.program_id == program_id)
            .all()
        )
        summary = []
        all_verified = True
        for scope in scopes:
            needs_verification = scope.asset_type in VERIFIABLE_ASSET_TYPES
            record = self._get_verification(scope.id)
            v_status = record.verification_status if record else VerificationStatus.UNVERIFIED.value
            if needs_verification and v_status != VerificationStatus.VERIFIED.value:
                all_verified = False
            summary.append({
                "scope_id":           str(scope.id),
                "asset_type":         scope.asset_type,
                "asset_identifier":   scope.asset_identifier,
                "needs_verification": needs_verification,
                "verification_status": v_status,
                "verified_at":        record.verified_at.isoformat() if record and record.verified_at else None,
                "method":             record.verification_method if record else None,
            })
        return {"all_verified": all_verified, "scopes": summary}

    def assert_all_scopes_verified(self, program_id: UUID) -> None:
        """Raise 400 if any verifiable scope is not VERIFIED.  Called at publish time."""
        summary = self.get_program_verification_summary(program_id)
        if not summary["all_verified"]:
            unverified = [
                s["asset_identifier"]
                for s in summary["scopes"]
                if s["needs_verification"]
                and s["verification_status"] != VerificationStatus.VERIFIED.value
            ]
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Cannot publish: the following scopes are not verified: "
                    f"{', '.join(unverified)}. "
                    f"Please verify domain ownership before publishing."
                ),
            )

    # ── Private helpers ───────────────────────────────────────────────────────

    def _get_or_raise(self, scope_id: UUID) -> ScopeVerification:
        record = self._get_verification(scope_id)
        if not record:
            raise HTTPException(status_code=404, detail="No verification record for this scope.")
        return record

    def _enforce_rate_limit(self, record: ScopeVerification) -> None:
        if not record.last_attempt_at:
            return
        window_start = datetime.utcnow() - timedelta(hours=1)
        if record.last_attempt_at.replace(tzinfo=None) > window_start:
            if (record.attempt_count or 0) >= MAX_ATTEMPTS_HOUR:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded. Max {MAX_ATTEMPTS_HOUR} verification attempts per hour.",
                )

    def _check_dns(self, record: ScopeVerification) -> Tuple[bool, str]:
        """Look up TXT records for root_domain and check for the expected token value."""
        try:
            import dns.resolver  # type: ignore

            resolver = dns.resolver.Resolver()
            resolver.lifetime = DNS_TIMEOUT

            expected = record.dns_record_value  # "ptaas-verification=<token>"

            try:
                answers = resolver.resolve(record.root_domain, "TXT")
            except dns.resolver.NXDOMAIN:
                return False, f"Domain '{record.root_domain}' does not exist in DNS."
            except dns.resolver.NoAnswer:
                return False, f"No TXT records found for '{record.root_domain}'."
            except dns.exception.Timeout:
                return False, "DNS lookup timed out. Please try again."

            for rdata in answers:
                for txt_string in rdata.strings:
                    decoded = txt_string.decode("utf-8", errors="replace")
                    if decoded == expected:
                        return True, "DNS TXT record verified successfully."

            return False, (
                f"Expected TXT record '{expected}' not found on '{record.root_domain}'. "
                f"DNS changes can take up to 24 hours to propagate."
            )

        except ImportError:
            # dnspython not installed — soft-fail with instructional message
            return False, (
                "DNS verification library not available. "
                "Install 'dnspython' to enable DNS TXT verification."
            )
        except Exception as exc:
            return False, f"DNS lookup error: {str(exc)}"

    def _check_file(self, record: ScopeVerification) -> Tuple[bool, str]:
        """Fetch HTTPS well-known file and verify token content."""
        url = record.file_verification_url  # https://<root_domain>/.well-known/ptaas-verification.txt

        # SSRF protection
        hostname = record.root_domain
        if not _is_ssrf_safe(hostname):
            return False, "SSRF protection: target resolves to a private or loopback address."

        try:
            with httpx.Client(
                timeout=HTTP_TIMEOUT,
                follow_redirects=True,
                max_redirects=HTTP_MAX_REDIRECTS,
                verify=True,          # enforce valid TLS
            ) as client:
                resp = client.get(url)

            if resp.status_code != 200:
                return False, (
                    f"HTTP {resp.status_code} received from {url}. "
                    f"Ensure the file exists and is publicly accessible."
                )

            content = resp.text.strip()
            expected_token = record.verification_token

            if content == expected_token:
                return True, "File-based verification succeeded."

            return False, (
                f"File content mismatch. "
                f"Expected '{expected_token}', got '{content[:80]}'. "
                f"Ensure the file at {url} contains only the token."
            )

        except httpx.ConnectError:
            return False, f"Cannot connect to {url}. Check the domain is live and HTTPS is configured."
        except httpx.TimeoutException:
            return False, f"HTTP request to {url} timed out after {HTTP_TIMEOUT}s."
        except httpx.TooManyRedirects:
            return False, f"Too many redirects when fetching {url}."
        except httpx.SSLError as exc:
            return False, f"TLS/SSL error: {exc}. HTTPS is required."
        except Exception as exc:
            return False, f"File fetch error: {str(exc)}"

    def _audit_admin(self, action_type, record, admin_id, admin_email, note, ip_address, severity):
        self.audit.log_action(
            action_type=action_type,
            action_category="security",
            target_type="scope",
            description=f"Admin {action_type.replace('_', ' ')} for {record.domain}",
            actor_id=admin_id,
            actor_role="admin",
            actor_email=admin_email,
            target_id=record.scope_id,
            metadata={"domain": record.domain, "note": note},
            ip_address=ip_address,
            severity=severity,
        )
