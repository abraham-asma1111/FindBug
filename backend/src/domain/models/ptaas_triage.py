"""
PTaaS Triage Models - FREQ-36
Triage specialist validation, prioritization, and reporting
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, JSON, Numeric
from sqlalchemy.orm import relationship
from src.core.database import Base


class PTaaSFindingTriage(Base):
    """Triage record for PTaaS findings - FREQ-36"""
    __tablename__ = "ptaas_finding_triage"

    id = Column(Integer, primary_key=True, index=True)
    finding_id = Column(Integer, ForeignKey("ptaas_findings.id"), nullable=False, unique=True)
    
    # Triage specialist validation
    triaged_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    triaged_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    triage_status = Column(String(50), default="PENDING")  # PENDING, VALIDATED, REJECTED, NEEDS_INFO
    triage_notes = Column(Text)
    
    # Prioritization
    priority_score = Column(Integer, nullable=False)  # 1-100
    priority_level = Column(String(50), nullable=False)  # CRITICAL, HIGH, MEDIUM, LOW
    priority_justification = Column(Text)
    
    # Risk assessment
    risk_rating = Column(String(50), nullable=False)  # CRITICAL, HIGH, MEDIUM, LOW
    likelihood = Column(String(50))  # CERTAIN, LIKELY, POSSIBLE, UNLIKELY
    impact_score = Column(Integer)  # 1-10
    exploitability_score = Column(Integer)  # 1-10
    
    # Compliance mapping
    compliance_frameworks = Column(JSON)  # List of applicable frameworks
    compliance_controls = Column(JSON)  # Specific controls violated
    regulatory_impact = Column(Text)
    
    # Evidence validation
    evidence_validated = Column(Boolean, default=False)
    evidence_quality = Column(String(50))  # EXCELLENT, GOOD, ADEQUATE, POOR
    evidence_notes = Column(Text)
    
    # Recommendations
    recommended_action = Column(String(100))  # IMMEDIATE_FIX, SCHEDULED_FIX, ACCEPT_RISK, FALSE_POSITIVE
    estimated_fix_time = Column(String(50))  # Hours/Days/Weeks
    
    # Executive summary
    executive_summary = Column(Text)
    business_context = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    finding = relationship("PTaaSFinding", backref="triage")


class PTaaSExecutiveReport(Base):
    """Executive report for PTaaS engagement - FREQ-36"""
    __tablename__ = "ptaas_executive_reports"

    id = Column(Integer, primary_key=True, index=True)
    engagement_id = Column(Integer, ForeignKey("ptaas_engagements.id"), nullable=False)
    
    report_title = Column(String(255), nullable=False)
    report_type = Column(String(50), default="EXECUTIVE")  # EXECUTIVE, TECHNICAL, COMPLIANCE
    
    # Report metadata
    generated_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    report_period_start = Column(DateTime)
    report_period_end = Column(DateTime)
    
    # Executive summary
    executive_summary = Column(Text, nullable=False)
    key_findings = Column(JSON)  # List of critical findings
    overall_risk_rating = Column(String(50), nullable=False)
    
    # Statistics
    total_findings = Column(Integer, default=0)
    critical_findings = Column(Integer, default=0)
    high_findings = Column(Integer, default=0)
    medium_findings = Column(Integer, default=0)
    low_findings = Column(Integer, default=0)
    
    # Risk metrics
    risk_score = Column(Numeric(5, 2))  # Overall risk score
    risk_trend = Column(String(50))  # INCREASING, STABLE, DECREASING
    
    # Compliance
    compliance_status = Column(JSON)  # Status per framework
    compliance_gaps = Column(JSON)  # List of compliance gaps
    compliance_recommendations = Column(Text)
    
    # Recommendations
    immediate_actions = Column(JSON)  # List of immediate actions
    short_term_actions = Column(JSON)  # 1-3 months
    long_term_actions = Column(JSON)  # 3+ months
    
    # Evidence and attachments
    evidence_summary = Column(JSON)  # Summary of evidence
    report_file_path = Column(String(500))  # Path to generated PDF/document
    report_file_url = Column(String(500))  # URL to download report
    
    # Approval workflow
    approved = Column(Boolean, default=False)
    approved_by = Column(Integer, ForeignKey("users.id"))
    approved_at = Column(DateTime)
    
    # Distribution
    distributed_to = Column(JSON)  # List of user IDs who received report
    distributed_at = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    engagement = relationship("PTaaSEngagement", backref="executive_reports")


class PTaaSFindingPrioritization(Base):
    """Prioritization history for findings - FREQ-36"""
    __tablename__ = "ptaas_finding_prioritization"

    id = Column(Integer, primary_key=True, index=True)
    finding_id = Column(Integer, ForeignKey("ptaas_findings.id"), nullable=False)
    
    prioritized_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    prioritized_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    old_priority = Column(String(50))
    new_priority = Column(String(50), nullable=False)
    
    reason = Column(Text)
    factors_considered = Column(JSON)  # List of factors
    
    created_at = Column(DateTime, default=datetime.utcnow)
