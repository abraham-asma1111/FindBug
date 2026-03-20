"""Audit Log domain model - FREQ-17."""
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Column, String, Text, DateTime, JSON, Index
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy import func

from src.core.database import Base


class AuditLog(Base):
    """
    Audit Log model - FREQ-17.
    
    Tracks all critical actions across the platform:
    - Report submissions
    - Status changes
    - Bounty awards
    - User actions
    - Admin actions
    - Configuration changes
    """
    
    __tablename__ = "audit_logs"
    
    # Primary identification
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Action details
    action_type = Column(String(100), nullable=False)
    # Types: report_submitted, report_status_changed, bounty_approved, 
    #        bounty_paid, user_created, user_deleted, program_created, 
    #        program_status_changed, config_updated, etc.
    
    action_category = Column(String(50), nullable=False)
    # Categories: report, bounty, user, program, admin, config, security
    
    # Actor (who performed the action)
    actor_id = Column(PGUUID(as_uuid=True), nullable=True)  # Null for system actions
    actor_role = Column(String(50), nullable=True)
    actor_email = Column(String(255), nullable=True)
    
    # Target (what was affected)
    target_type = Column(String(50), nullable=False)
    # Types: report, user, program, organization, bounty, config
    
    target_id = Column(PGUUID(as_uuid=True), nullable=True)
    
    # Action details
    description = Column(Text, nullable=False)
    
    # Additional metadata (JSON)
    metadata = Column(JSONB, nullable=True)
    # Stores: old_value, new_value, reason, ip_address, user_agent, etc.
    
    # Request context
    ip_address = Column(String(45), nullable=True)  # IPv6 support
    user_agent = Column(String(500), nullable=True)
    
    # Severity level
    severity = Column(String(20), nullable=False, server_default="info")
    # Levels: info, warning, critical
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Indexes for performance
    __table_args__ = (
        Index('ix_audit_logs_action_type', 'action_type'),
        Index('ix_audit_logs_action_category', 'action_category'),
        Index('ix_audit_logs_actor_id', 'actor_id'),
        Index('ix_audit_logs_target_type', 'target_type'),
        Index('ix_audit_logs_target_id', 'target_id'),
        Index('ix_audit_logs_created_at', 'created_at'),
        Index('ix_audit_logs_severity', 'severity'),
    )
