"""
Operational / Platform Models — FREQ-12, FREQ-15, FREQ-22, FREQ-42
webhook_endpoints:  org-registered webhook URLs
webhook_logs:       delivery attempt records per webhook
email_templates:    reusable notification email templates
data_exports:       async export job tracking
compliance_reports: generated compliance/audit reports
Aligned with ERD extended tables
"""
import uuid
from datetime import datetime

from sqlalchemy import Column, String, Boolean, Integer, BigInteger, DateTime, Text, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from src.core.database import Base


class WebhookEndpoint(Base):
    """
    Webhook Endpoint — ERD: webhook_endpoints
    Organizations register URLs to receive real-time event notifications.
    """
    __tablename__ = "webhook_endpoints"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"),
                             nullable=False, index=True)

    url = Column(String(500), nullable=False)
    secret = Column(String(100), nullable=True)   # HMAC signing secret
    events = Column(JSONB, nullable=False, default=list)
    # e.g. ["report.submitted", "bounty.approved", "program.published"]

    is_active = Column(Boolean, nullable=False, default=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    organization = relationship("Organization", back_populates="webhook_endpoints")
    logs = relationship("WebhookLog", back_populates="endpoint", cascade="all, delete-orphan")


class WebhookLog(Base):
    """
    Webhook Log — ERD: webhook_logs
    One record per delivery attempt for a webhook event.
    """
    __tablename__ = "webhook_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    endpoint_id = Column(UUID(as_uuid=True), ForeignKey("webhook_endpoints.id", ondelete="CASCADE"),
                         nullable=False, index=True)

    event = Column(String(100), nullable=False)
    payload = Column(JSONB, nullable=True)
    response_status = Column(Integer, nullable=True)
    response_body = Column(Text, nullable=True)
    error_message = Column(String(500), nullable=True)
    retry_count = Column(Integer, nullable=False, default=0)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_webhook_logs_created_at", "created_at"),
    )

    endpoint = relationship("WebhookEndpoint", back_populates="logs")


class EmailTemplate(Base):
    """
    Email Template — ERD: email_templates
    Reusable HTML/text templates for all platform notification emails.
    """
    __tablename__ = "email_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    name = Column(String(100), nullable=False, unique=True)
    # e.g. "report_submitted", "bounty_approved", "kyc_verified"

    subject = Column(String(200), nullable=False)
    body_html = Column(Text, nullable=False)
    body_text = Column(Text, nullable=True)
    variables = Column(JSONB, nullable=True)
    # e.g. ["researcher_name", "report_title", "amount"]

    is_active = Column(Boolean, nullable=False, default=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)


class DataExport(Base):
    """
    Data Export — ERD: data_exports
    Tracks async export jobs (CSV/PDF/JSON) requested by users.
    """
    __tablename__ = "data_exports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"),
                     nullable=False, index=True)

    export_type = Column(String(50), nullable=False)
    # reports | payments | analytics | audit_logs | program_data

    format = Column(String(20), nullable=False, default="csv")
    # csv | json | pdf | xlsx

    filters = Column(JSONB, nullable=True)   # query filters applied
    file_path = Column(String(500), nullable=True)
    file_size = Column(BigInteger, nullable=True)

    # pending | processing | completed | failed | expired
    status = Column(String(20), nullable=False, default="pending", index=True)

    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="data_exports")


class ComplianceReport(Base):
    """
    Compliance Report — ERD: compliance_reports
    Generated compliance/audit reports (PCI-DSS, ISO 27001, etc.).
    """
    __tablename__ = "compliance_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    report_type = Column(String(100), nullable=False)
    # pci_dss | iso_27001 | soc2 | hipaa | platform_audit

    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    data = Column(JSONB, nullable=True)
    file_path = Column(String(500), nullable=True)

    generated_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    generated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    generator = relationship("User", foreign_keys=[generated_by])
