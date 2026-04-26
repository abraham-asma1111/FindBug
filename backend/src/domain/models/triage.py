"""
Triage & Validation Models — FREQ-07, FREQ-08
triage_queue:         incoming report queue with priority
triage_assignments:   which specialist handles which report
validation_results:   outcome of triage (severity, CVSS, reward recommendation)
duplicate_detections: detected duplicate reports
Aligned with ERD: triage_queue, triage_assignments, validation_results, duplicate_detections
"""
import uuid
from datetime import datetime

from sqlalchemy import Column, String, Integer, Boolean, DateTime, DECIMAL, Text, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.core.database import Base


class TriageQueue(Base):
    """
    Triage Queue — ERD: triage_queue
    Every submitted report gets a queue entry with a priority score.
    """
    __tablename__ = "triage_queue"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id = Column(UUID(as_uuid=True), ForeignKey("vulnerability_reports.id", ondelete="CASCADE"),
                       nullable=False, unique=True, index=True)

    priority = Column(Integer, nullable=False, default=5)  # 1 (highest) – 10 (lowest)
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # pending | assigned | in_review | completed | escalated
    status = Column(String(20), nullable=False, default="pending", index=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    assigned_at = Column(DateTime, nullable=True)

    # Relationships
    report = relationship("VulnerabilityReport", back_populates="triage_queue_entry")
    assignee = relationship("User", foreign_keys=[assigned_to])


class TriageAssignment(Base):
    """
    Triage Assignment — ERD: triage_assignments
    Tracks the full history of specialist assignments per report.
    """
    __tablename__ = "triage_assignments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id = Column(UUID(as_uuid=True), ForeignKey("vulnerability_reports.id", ondelete="CASCADE"),
                       nullable=False, index=True)
    specialist_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"),
                           nullable=True, index=True)

    # pending | in_progress | completed | reassigned
    status = Column(String(20), nullable=False, default="pending")

    assigned_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    report = relationship("VulnerabilityReport", back_populates="triage_assignments")
    specialist = relationship("User", foreign_keys=[specialist_id])


class ValidationResult(Base):
    """
    Validation Result — ERD: validation_results
    The triage specialist's formal verdict on a report.
    """
    __tablename__ = "validation_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id = Column(UUID(as_uuid=True), ForeignKey("vulnerability_reports.id", ondelete="CASCADE"),
                       nullable=False, index=True)
    validator_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"),
                          nullable=True)

    is_valid = Column(Boolean, nullable=False)
    severity_rating = Column(String(20), nullable=True)   # critical | high | medium | low | informational
    cvss_score = Column(DECIMAL(3, 1), nullable=True)
    recommended_reward = Column(DECIMAL(15, 2), nullable=True)
    notes = Column(Text, nullable=True)

    validated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    report = relationship("VulnerabilityReport", back_populates="validation_result")
    validator = relationship("User", foreign_keys=[validator_id])


class DuplicateDetection(Base):
    """
    Duplicate Detection — ERD: duplicate_detections
    Records when a report is flagged as a duplicate of an existing one.
    """
    __tablename__ = "duplicate_detections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id = Column(UUID(as_uuid=True), ForeignKey("vulnerability_reports.id", ondelete="CASCADE"),
                       nullable=False, index=True)
    duplicate_of = Column(UUID(as_uuid=True), ForeignKey("vulnerability_reports.id", ondelete="CASCADE"),
                          nullable=False, index=True)

    similarity_score = Column(DECIMAL(5, 2), nullable=True)  # 0.00 – 100.00
    detection_method = Column(String(50), nullable=False, default="manual")
    # manual | automated | hash_match | semantic_similarity

    detected_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    report = relationship("VulnerabilityReport", foreign_keys=[report_id],
                          back_populates="duplicate_detections")
    original_report = relationship("VulnerabilityReport", foreign_keys=[duplicate_of])


class TriageTemplate(Base):
    """
    Triage Template — Response templates for triage specialists
    Pre-written messages for common triage scenarios (validation, rejection, duplicate, etc.)
    """
    __tablename__ = "triage_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(50), nullable=False, index=True)
    # validation | rejection | duplicate | need_info | resolved
    
    is_active = Column(Boolean, nullable=False, default=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
