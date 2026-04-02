"""Notification Model - FREQ-12."""
from sqlalchemy import Column, String, Boolean, DateTime, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
import enum

from src.core.database import Base


class NotificationType(str, enum.Enum):
    """Notification types for different events."""
    # Report events
    REPORT_SUBMITTED = "report_submitted"
    REPORT_STATUS_CHANGED = "report_status_changed"
    REPORT_TRIAGED = "report_triaged"
    REPORT_VALIDATED = "report_validated"
    REPORT_INVALID = "report_invalid"
    REPORT_DUPLICATE = "report_duplicate"
    REPORT_RESOLVED = "report_resolved"
    REPORT_ACKNOWLEDGED = "report_acknowledged"
    
    # Bounty events
    BOUNTY_APPROVED = "bounty_approved"
    BOUNTY_REJECTED = "bounty_rejected"
    BOUNTY_PAID = "bounty_paid"
    
    # Reputation events
    REPUTATION_UPDATED = "reputation_updated"
    RANK_CHANGED = "rank_changed"
    
    # Message events
    NEW_MESSAGE = "new_message"
    NEW_COMMENT = "new_comment"
    
    # Program events
    PROGRAM_PUBLISHED = "program_published"
    PROGRAM_UPDATED = "program_updated"
    PROGRAM_CLOSED = "program_closed"
    
    # System events
    ACCOUNT_VERIFIED = "account_verified"
    PASSWORD_CHANGED = "password_changed"
    MFA_ENABLED = "mfa_enabled"
    
    # KYC events
    KYC_SUBMITTED = "kyc_submitted"
    KYC_APPROVED = "kyc_approved"
    KYC_REJECTED = "kyc_rejected"
    KYC_EXPIRED = "kyc_expired"
    
    # Matching events
    MATCH_FOUND = "match_found"
    ASSIGNMENT_APPROVED = "assignment_approved"
    ASSIGNMENT_REJECTED = "assignment_rejected"
    
    # Security events
    SECURITY_INCIDENT = "security_incident"


class NotificationPriority(str, enum.Enum):
    """Notification priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Notification(Base):
    """
    In-platform notification model - FREQ-12.
    
    Stores notifications for users about key events.
    """
    __tablename__ = "notifications"
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Recipient
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Notification Details
    notification_type = Column(SQLEnum(NotificationType, values_callable=lambda x: [e.value for e in x]), nullable=False)
    priority = Column(SQLEnum(NotificationPriority, values_callable=lambda x: [e.value for e in x]), default=NotificationPriority.MEDIUM)
    
    # Content
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    
    # Related Entity (optional)
    related_entity_type = Column(String(50), nullable=True)  # 'report', 'program', 'bounty', etc.
    related_entity_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Action Link (optional)
    action_url = Column(String(500), nullable=True)
    action_text = Column(String(100), nullable=True)
    
    # Status
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime, nullable=True)
    
    # Email Status
    email_sent = Column(Boolean, default=False)
    email_sent_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    expires_at = Column(DateTime, nullable=True)  # Optional expiration
    
    def __repr__(self):
        return f"<Notification {self.notification_type} for user {self.user_id}>"
