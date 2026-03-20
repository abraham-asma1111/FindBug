"""
PTaaS Retest Models - FREQ-37
Free retesting of fixed vulnerabilities
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from backend.src.core.database import Base


class PTaaSRetestRequest(Base):
    """Retest request for fixed vulnerabilities - FREQ-37"""
    __tablename__ = "ptaas_retest_requests"

    id = Column(Integer, primary_key=True, index=True)
    finding_id = Column(Integer, ForeignKey("ptaas_findings.id"), nullable=False)
    engagement_id = Column(Integer, ForeignKey("ptaas_engagements.id"), nullable=False)
    
    # Request details
    requested_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    requested_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    status = Column(String(50), default="PENDING")  # PENDING, APPROVED, IN_PROGRESS, COMPLETED, REJECTED, EXPIRED
    
    # Fix details
    fix_description = Column(Text, nullable=False)
    fix_implemented_at = Column(DateTime)
    fix_evidence = Column(JSON)  # URLs to evidence of fix
    
    # Retest assignment
    assigned_to = Column(Integer, ForeignKey("users.id"))
    assigned_at = Column(DateTime)
    
    # Retest results
    retest_started_at = Column(DateTime)
    retest_completed_at = Column(DateTime)
    retest_result = Column(String(50))  # FIXED, NOT_FIXED, PARTIALLY_FIXED, NEW_ISSUE
    retest_notes = Column(Text)
    retest_evidence = Column(JSON)  # URLs to retest evidence
    
    # Eligibility tracking
    is_eligible = Column(Boolean, default=True)
    eligibility_expires_at = Column(DateTime, nullable=False)
    eligibility_reason = Column(Text)
    
    # Free retest tracking
    is_free_retest = Column(Boolean, default=True)
    retest_count = Column(Integer, default=1)  # Track number of retests
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    finding = relationship("PTaaSFinding", backref="retest_requests")
    engagement = relationship("PTaaSEngagement", backref="retest_requests")


class PTaaSRetestPolicy(Base):
    """Retest policy configuration - FREQ-37"""
    __tablename__ = "ptaas_retest_policies"

    id = Column(Integer, primary_key=True, index=True)
    engagement_id = Column(Integer, ForeignKey("ptaas_engagements.id"), nullable=False, unique=True)
    
    # Policy settings
    retest_period_months = Column(Integer, default=12, nullable=False)
    max_free_retests_per_finding = Column(Integer, default=3)
    
    # Eligibility criteria
    eligible_severities = Column(JSON)  # List of severities eligible for retest
    requires_fix_evidence = Column(Boolean, default=True)
    requires_approval = Column(Boolean, default=False)
    
    # Turnaround time
    target_turnaround_days = Column(Integer, default=5)
    
    # Restrictions
    allow_partial_fixes = Column(Boolean, default=True)
    allow_new_findings_during_retest = Column(Boolean, default=True)
    
    # Notifications
    notify_on_request = Column(Boolean, default=True)
    notify_on_completion = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    engagement = relationship("PTaaSEngagement", backref="retest_policy")


class PTaaSRetestHistory(Base):
    """Historical record of retest activities - FREQ-37"""
    __tablename__ = "ptaas_retest_history"

    id = Column(Integer, primary_key=True, index=True)
    retest_request_id = Column(Integer, ForeignKey("ptaas_retest_requests.id"), nullable=False)
    finding_id = Column(Integer, ForeignKey("ptaas_findings.id"), nullable=False)
    
    # Activity tracking
    activity_type = Column(String(50), nullable=False)  # REQUESTED, APPROVED, ASSIGNED, STARTED, COMPLETED, REJECTED
    activity_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    activity_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Activity details
    previous_status = Column(String(50))
    new_status = Column(String(50))
    notes = Column(Text)
    metadata = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    retest_request = relationship("PTaaSRetestRequest", backref="history")
