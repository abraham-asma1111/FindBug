"""
Code Review Domain Models
Implements FREQ-41: Expert Code Review System
"""
from sqlalchemy import Column, String, Integer, Text, ForeignKey, TIMESTAMP, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from src.core.database import Base


class ReviewType(str, enum.Enum):
    """Code review types"""
    SECURITY = "security"
    PERFORMANCE = "performance"
    BEST_PRACTICES = "best_practices"
    ARCHITECTURE = "architecture"
    FULL_REVIEW = "full_review"


class ReviewStatus(str, enum.Enum):
    """Code review engagement status"""
    PENDING = "pending"
    MATCHING = "matching"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    UNDER_REVIEW = "under_review"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class FindingSeverity(str, enum.Enum):
    """Code review finding severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class FindingStatus(str, enum.Enum):
    """Code review finding status"""
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    FIXED = "fixed"
    WONT_FIX = "wont_fix"
    FALSE_POSITIVE = "false_positive"


class IssueType(str, enum.Enum):
    """Types of code issues"""
    DEAD_CODE = "dead_code"
    INSECURE_DEPENDENCY = "insecure_dependency"
    LOGIC_FLAW = "logic_flaw"
    SECURITY_VULNERABILITY = "security_vulnerability"
    PERFORMANCE_ISSUE = "performance_issue"
    CODE_SMELL = "code_smell"
    MEMORY_LEAK = "memory_leak"
    RACE_CONDITION = "race_condition"
    OTHER = "other"


class CodeReviewEngagement(Base):
    """Code review engagement model"""
    __tablename__ = "code_review_engagements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    reviewer_id = Column(UUID(as_uuid=True), ForeignKey("researchers.id"), nullable=True)
    
    title = Column(String(200), nullable=False)
    repository_url = Column(String(500), nullable=False)
    review_type = Column(SQLEnum(ReviewType), nullable=False)
    status = Column(SQLEnum(ReviewStatus), nullable=False, default=ReviewStatus.PENDING)
    
    findings_count = Column(Integer, default=0)
    report_submitted_at = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    
    # Relationships
    findings = relationship("CodeReviewFinding", back_populates="engagement", cascade="all, delete-orphan")


class CodeReviewFinding(Base):
    """Code review finding model"""
    __tablename__ = "code_review_findings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    engagement_id = Column(UUID(as_uuid=True), ForeignKey("code_review_engagements.id"), nullable=False)
    
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(SQLEnum(FindingSeverity), nullable=False)
    issue_type = Column(SQLEnum(IssueType), nullable=False)
    
    file_path = Column(String(500), nullable=True)
    line_number = Column(Integer, nullable=True)
    
    status = Column(SQLEnum(FindingStatus), nullable=False, default=FindingStatus.OPEN)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    
    # Relationships
    engagement = relationship("CodeReviewEngagement", back_populates="findings")
