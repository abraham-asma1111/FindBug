"""Scope Verification domain model — per-scope domain ownership verification."""
import enum
from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    Column, String, Text, DateTime, ForeignKey, Index, Integer
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship
from sqlalchemy import func

from src.core.database import Base


class VerificationStatus(str, enum.Enum):
    UNVERIFIED = "unverified"
    PENDING    = "pending"
    VERIFIED   = "verified"
    FAILED     = "failed"
    SUSPENDED  = "suspended"
    EXPIRED    = "expired"


class VerificationMethod(str, enum.Enum):
    DNS_TXT    = "dns_txt"
    FILE_BASED = "file_based"


class ScopeVerification(Base):
    """
    Per-scope domain ownership verification record.

    One record per (scope_id, domain) pair.  The same scope can be
    re-verified — the record is updated in-place rather than recreated.

    Verification flow:
        UNVERIFIED → PENDING → VERIFIED
                             → FAILED     (token check failed)
        VERIFIED   → SUSPENDED (reverification failed)
        ANY        → EXPIRED   (token TTL exceeded)
    """

    __tablename__ = "scope_verifications"

    # ── Primary key ────────────────────────────────────────────────────────
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # ── Scope linkage ───────────────────────────────────────────────────────
    scope_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("program_scopes.id", ondelete="CASCADE"),
        nullable=False
    )
    program_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("bounty_programs.id", ondelete="CASCADE"),
        nullable=False
    )
    organization_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False
    )

    # ── Domain info ─────────────────────────────────────────────────────────
    domain      = Column(String(500), nullable=False)   # full asset_identifier
    root_domain = Column(String(255), nullable=False)   # extracted root (e.g. company.com)

    # ── Verification method & token ─────────────────────────────────────────
    verification_method = Column(String(20), nullable=False)   # dns_txt | file_based
    verification_token  = Column(String(100), nullable=False)  # ptaas-verification=<hex>

    # ── State ───────────────────────────────────────────────────────────────
    verification_status = Column(
        String(20),
        nullable=False,
        server_default=VerificationStatus.UNVERIFIED.value
    )

    # ── Timestamps ──────────────────────────────────────────────────────────
    verified_at  = Column(DateTime(timezone=True), nullable=True)
    expires_at   = Column(DateTime(timezone=True), nullable=True)  # token TTL
    last_checked = Column(DateTime(timezone=True), nullable=True)
    created_at   = Column(DateTime(timezone=True), server_default=func.now())
    updated_at   = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # ── Failure tracking ────────────────────────────────────────────────────
    failure_reason     = Column(Text, nullable=True)
    attempt_count      = Column(Integer, nullable=False, server_default="0")
    last_attempt_at    = Column(DateTime(timezone=True), nullable=True)

    # ── Actor ───────────────────────────────────────────────────────────────
    created_by = Column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True
    )

    # ── Admin moderation ────────────────────────────────────────────────────
    admin_note    = Column(Text, nullable=True)
    moderated_by  = Column(PGUUID(as_uuid=True), nullable=True)
    moderated_at  = Column(DateTime(timezone=True), nullable=True)

    # ── Relationships ────────────────────────────────────────────────────────
    scope = relationship("ProgramScope", back_populates="verifications", lazy="select")

    # ── Indexes ──────────────────────────────────────────────────────────────
    __table_args__ = (
        Index("ix_sv_scope_id",   "scope_id"),
        Index("ix_sv_domain",     "domain"),
        Index("ix_sv_root_domain","root_domain"),
        Index("ix_sv_status",     "verification_status"),
        Index("ix_sv_org_id",     "organization_id"),
        Index("ix_sv_expires_at", "expires_at"),
    )

    # ── Helpers ───────────────────────────────────────────────────────────────
    @property
    def is_verified(self) -> bool:
        return self.verification_status == VerificationStatus.VERIFIED.value

    @property
    def is_token_expired(self) -> bool:
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at.replace(tzinfo=None)

    @property
    def dns_record_name(self) -> str:
        """Expected DNS TXT record host."""
        return self.root_domain

    @property
    def dns_record_value(self) -> str:
        """Expected DNS TXT record value."""
        return f"ptaas-verification={self.verification_token}"

    @property
    def file_verification_url(self) -> str:
        """Expected file URL for file-based verification."""
        return f"https://{self.root_domain}/.well-known/ptaas-verification.txt"
