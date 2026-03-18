"""Vulnerability Report domain models."""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import (
    Column, String, Text, DateTime, Numeric, Integer, Boolean,
    ForeignKey, func, Index
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship

from src.core.database import Base


class VulnerabilityReport(Base):
    """Vulnerability Report model - FREQ-06, FREQ-07, FREQ-08."""
    
    __tablename__ = "vulnerability_reports"
    
    # Primary identification
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    report_number = Column(String(50), unique=True, nullable=False)  # e.g., REP-2026-001
    
    # Relationships
    program_id = Column(PGUUID(as_uuid=True), ForeignKey("bounty_programs.id", ondelete="CASCADE"), nullable=False)
    researcher_id = Column(PGUUID(as_uuid=True), ForeignKey("researchers.id", ondelete="CASCADE"), nullable=False)
    
    # Report content - FREQ-06
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    steps_to_reproduce = Column(Text, nullable=False)
    impact_assessment = Column(Text, nullable=False)
    suggested_severity = Column(String(20), nullable=False)  # critical, high, medium, low
    
    # Asset information
    affected_asset = Column(String(500), nullable=True)  # Which scope item
    vulnerability_type = Column(String(100), nullable=True)  # XSS, SQLi, CSRF, etc.
    
    # Triage and validation - FREQ-07, FREQ-08
    status = Column(String(20), nullable=False, server_default="new")  
    # Status flow: new → triaged → valid/invalid/duplicate → resolved/closed
    
    assigned_severity = Column(String(20), nullable=True)  # Assigned by triage specialist
    cvss_score = Column(Numeric(3, 1), nullable=True)  # CVSS score (0.0-10.0)
    vrt_category = Column(String(100), nullable=True)  # VRT taxonomy category
    
    # Triage information
    triaged_by = Column(PGUUID(as_uuid=True), ForeignKey("staff.id"), nullable=True)
    triaged_at = Column(DateTime(timezone=True), nullable=True)
    triage_notes = Column(Text, nullable=True)
    
    # Duplicate handling - BR-07
    is_duplicate = Column(Boolean, nullable=False, server_default="false")
    duplicate_of = Column(PGUUID(as_uuid=True), ForeignKey("vulnerability_reports.id"), nullable=True)
    duplicate_detected_at = Column(DateTime(timezone=True), nullable=True)
    
    # Disclosure timeline - BR-10
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)  # Must be within 24 hours
    remediation_deadline = Column(DateTime(timezone=True), nullable=True)  # 90 days from acknowledgment
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    public_disclosure_date = Column(DateTime(timezone=True), nullable=True)
    
    # Bounty information - FREQ-10
    bounty_amount = Column(Numeric(15, 2), nullable=True)
    bounty_status = Column(String(20), nullable=True)  # pending, approved, paid
    bounty_approved_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    bounty_approved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Collaboration - FREQ-09
    last_activity_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Metadata
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    closed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    program = relationship("BountyProgram")
    researcher = relationship("Researcher")
    triage_specialist = relationship("Staff", foreign_keys=[triaged_by])
    bounty_approver = relationship("User", foreign_keys=[bounty_approved_by])
    attachments = relationship("ReportAttachment", back_populates="report", cascade="all, delete-orphan")
    comments = relationship("ReportComment", back_populates="report", cascade="all, delete-orphan")
    duplicate_reports = relationship(
        "VulnerabilityReport",
        foreign_keys=[duplicate_of],
        remote_side=[id],
        backref="original_report"
    )
    
    # Indexes for performance
    __table_args__ = (
        Index('ix_vulnerability_reports_program_id', 'program_id'),
        Index('ix_vulnerability_reports_researcher_id', 'researcher_id'),
        Index('ix_vulnerability_reports_status', 'status'),
        Index('ix_vulnerability_reports_severity', 'assigned_severity'),
        Index('ix_vulnerability_reports_submitted_at', 'submitted_at'),
        Index('ix_vulnerability_reports_report_number', 'report_number'),
    )


class ReportAttachment(Base):
    """Report Attachment model - FREQ-06, FREQ-21."""
    
    __tablename__ = "report_attachments"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    report_id = Column(PGUUID(as_uuid=True), ForeignKey("vulnerability_reports.id", ondelete="CASCADE"), nullable=False)
    
    # File information
    filename = Column(String(500), nullable=False)
    original_filename = Column(String(500), nullable=False)
    file_type = Column(String(100), nullable=False)  # image/png, video/mp4, text/plain
    file_size = Column(Integer, nullable=False)  # bytes
    storage_path = Column(String(1000), nullable=False)  # S3 path or local path
    
    # Security
    is_safe = Column(Boolean, nullable=False, server_default="false")  # Virus scan result
    scanned_at = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    uploaded_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    report = relationship("VulnerabilityReport", back_populates="attachments")
    uploader = relationship("User")
    
    __table_args__ = (
        Index('ix_report_attachments_report_id', 'report_id'),
    )


class ReportComment(Base):
    """Report Comment model - FREQ-09 (secure messaging/collaboration)."""
    
    __tablename__ = "report_comments"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    report_id = Column(PGUUID(as_uuid=True), ForeignKey("vulnerability_reports.id", ondelete="CASCADE"), nullable=False)
    
    # Comment content
    comment_text = Column(Text, nullable=False)
    comment_type = Column(String(20), nullable=False, server_default="comment")  
    # Types: comment, status_change, severity_change, internal_note
    
    is_internal = Column(Boolean, nullable=False, server_default="false")  
    # Internal notes only visible to triage/org, not researcher
    
    # Author
    author_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    author_role = Column(String(50), nullable=False)  # researcher, triage_specialist, organization, admin
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    edited = Column(Boolean, nullable=False, server_default="false")
    
    # Relationships
    report = relationship("VulnerabilityReport", back_populates="comments")
    author = relationship("User")
    
    __table_args__ = (
        Index('ix_report_comments_report_id', 'report_id'),
        Index('ix_report_comments_created_at', 'created_at'),
    )


class ReportStatusHistory(Base):
    """Report Status History model - FREQ-17 (audit trail)."""
    
    __tablename__ = "report_status_history"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    report_id = Column(PGUUID(as_uuid=True), ForeignKey("vulnerability_reports.id", ondelete="CASCADE"), nullable=False)
    
    # Status change
    from_status = Column(String(20), nullable=True)
    to_status = Column(String(20), nullable=False)
    change_reason = Column(Text, nullable=True)
    
    # Actor
    changed_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    changed_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    report = relationship("VulnerabilityReport")
    changer = relationship("User")
    
    __table_args__ = (
        Index('ix_report_status_history_report_id', 'report_id'),
        Index('ix_report_status_history_changed_at', 'changed_at'),
    )
