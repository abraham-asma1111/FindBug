"""Analytics Models - FREQ-15, Extended ERD."""
from sqlalchemy import Column, String, Integer, DateTime, Date, Numeric, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from src.core.database import Base


class ResearcherMetrics(Base):
    """
    Researcher Metrics Model - Extended ERD.
    
    Tracks researcher performance metrics for analytics.
    """
    __tablename__ = "researcher_metrics"
    
    # Primary Key
    metrics_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign Key
    researcher_id = Column(UUID(as_uuid=True), ForeignKey('researchers.id'), nullable=False, index=True)
    
    # Metrics
    total_reports = Column(Integer, default=0)
    validated_reports = Column(Integer, default=0)
    invalid_reports = Column(Integer, default=0)
    duplicate_reports = Column(Integer, default=0)
    success_rate = Column(Numeric(5, 2), default=0.0)  # Percentage
    reputation_score = Column(Numeric(10, 2), default=0.0)
    total_earnings = Column(Numeric(15, 2), default=0.0)
    rank = Column(Integer, nullable=True)
    
    # Severity breakdown
    critical_reports = Column(Integer, default=0)
    high_reports = Column(Integer, default=0)
    medium_reports = Column(Integer, default=0)
    low_reports = Column(Integer, default=0)
    
    # Time metrics
    avg_time_to_triage_hours = Column(Numeric(10, 2), nullable=True)
    avg_time_to_resolve_days = Column(Numeric(10, 2), nullable=True)
    
    # Timestamps
    last_calculated_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<ResearcherMetrics researcher_id={self.researcher_id} total_reports={self.total_reports}>"


class OrganizationMetrics(Base):
    """
    Organization Metrics Model - Extended ERD.
    
    Tracks organization analytics and program performance.
    """
    __tablename__ = "organization_metrics"
    
    # Primary Key
    metrics_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign Key
    organization_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id'), nullable=False, index=True)
    
    # Program metrics
    total_programs = Column(Integer, default=0)
    active_programs = Column(Integer, default=0)
    
    # Report metrics
    total_reports_received = Column(Integer, default=0)
    validated_reports = Column(Integer, default=0)
    invalid_reports = Column(Integer, default=0)
    resolved_reports = Column(Integer, default=0)
    
    # Time metrics (Mean Time To Resolve)
    mttr_hours = Column(Numeric(10, 2), nullable=True)  # Mean Time To Resolve
    avg_triage_time_hours = Column(Numeric(10, 2), nullable=True)
    
    # Financial metrics
    total_bounties_paid = Column(Numeric(15, 2), default=0.0)
    total_bounties_pending = Column(Numeric(15, 2), default=0.0)
    platform_commission_paid = Column(Numeric(15, 2), default=0.0)
    roi = Column(Numeric(10, 2), nullable=True)  # Return on Investment
    
    # Severity breakdown
    critical_reports = Column(Integer, default=0)
    high_reports = Column(Integer, default=0)
    medium_reports = Column(Integer, default=0)
    low_reports = Column(Integer, default=0)
    
    # Timestamps
    last_calculated_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<OrganizationMetrics org_id={self.organization_id} total_reports={self.total_reports_received}>"


class PlatformMetrics(Base):
    """
    Platform Metrics Model - Extended ERD.
    
    Tracks platform-wide statistics and growth metrics.
    """
    __tablename__ = "platform_metrics"
    
    # Primary Key
    metrics_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Date for time-series data
    date = Column(Date, nullable=False, unique=True, index=True)
    
    # User metrics
    total_users = Column(Integer, default=0)
    total_researchers = Column(Integer, default=0)
    total_organizations = Column(Integer, default=0)
    active_users = Column(Integer, default=0)
    new_users = Column(Integer, default=0)
    
    # Program metrics
    total_programs = Column(Integer, default=0)
    active_programs = Column(Integer, default=0)
    new_programs = Column(Integer, default=0)
    
    # Report metrics
    total_reports = Column(Integer, default=0)
    new_reports = Column(Integer, default=0)
    validated_reports = Column(Integer, default=0)
    resolved_reports = Column(Integer, default=0)
    
    # Financial metrics
    total_bounties_paid = Column(Numeric(15, 2), default=0.0)
    platform_revenue = Column(Numeric(15, 2), default=0.0)  # 30% commission
    total_transactions = Column(Integer, default=0)
    
    # Performance metrics
    avg_triage_time_hours = Column(Numeric(10, 2), nullable=True)
    avg_resolution_time_days = Column(Numeric(10, 2), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<PlatformMetrics date={self.date} total_users={self.total_users}>"


class AnalyticsReport(Base):
    """
    Analytics Report Model - Extended ERD.
    
    Stores custom analytics reports generated by the system.
    """
    __tablename__ = "analytics_reports"
    
    # Primary Key
    report_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Report details
    report_type = Column(String(50), nullable=False)  # vulnerability_trends, program_effectiveness, researcher_performance
    report_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Filters and parameters
    filters = Column(Text, nullable=True)  # JSON string of filters applied
    time_period = Column(String(20), nullable=True)  # 7days, 30days, 6months, etc.
    
    # Report data (stored as JSON)
    report_data = Column(Text, nullable=False)  # JSON string of report results
    
    # Metadata
    generated_by = Column(UUID(as_uuid=True), nullable=True)  # User who generated
    generated_for = Column(UUID(as_uuid=True), nullable=True)  # Organization/Researcher
    
    # Timestamps
    generated_at = Column(DateTime, default=datetime.utcnow, index=True)
    expires_at = Column(DateTime, nullable=True)  # Optional expiration
    
    def __repr__(self):
        return f"<AnalyticsReport type={self.report_type} generated_at={self.generated_at}>"
