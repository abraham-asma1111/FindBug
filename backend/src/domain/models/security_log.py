"""
Security Log Models — FREQ-02, FREQ-17
security_events: suspicious/blocked activity tracking
login_history:   per-login authentication record
Aligned with ERD: security_events, login_history
"""
import uuid
from datetime import datetime

from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.core.database import Base


class SecurityEvent(Base):
    """
    Security Event — ERD: security_events
    Records suspicious activity: brute force, SSRF attempts, anomalous access, etc.
    """
    __tablename__ = "security_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

    event_type = Column(String(100), nullable=False, index=True)
    # e.g. brute_force, account_lockout, suspicious_ip, mfa_bypass_attempt,
    #      rate_limit_exceeded, ssrf_attempt, xss_attempt

    severity = Column(String(20), nullable=False, default="medium", index=True)
    # low | medium | high | critical

    description = Column(Text, nullable=False)
    ip_address = Column(String(45), nullable=True)
    is_blocked = Column(Boolean, nullable=False, default=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_security_events_created_at", "created_at"),
    )

    user = relationship("User", back_populates="security_events")


class LoginHistory(Base):
    """
    Login History — ERD: login_history
    One record per login attempt (success or failure).
    """
    __tablename__ = "login_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    is_successful = Column(Boolean, nullable=False, default=False)
    failure_reason = Column(String(200), nullable=True)
    # e.g. invalid_password | account_locked | mfa_failed | unverified_email
    mfa_used = Column(Boolean, nullable=False, default=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_login_history_created_at", "created_at"),
    )

    user = relationship("User", back_populates="login_history")
