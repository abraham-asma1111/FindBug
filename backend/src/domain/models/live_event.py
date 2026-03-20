"""
Live Hacking Events Domain Models
Implements FREQ-43, FREQ-44: Live Hacking Events with Real-time Dashboards
"""
from sqlalchemy import Column, String, Integer, Text, ForeignKey, TIMESTAMP, Enum as SQLEnum, DECIMAL, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from backend.src.core.database import Base


class EventStatus(str, enum.Enum):
    """Live hacking event status"""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    CLOSED = "closed"
    ARCHIVED = "archived"


class ParticipationStatus(str, enum.Enum):
    """Event participation status"""
    INVITED = "invited"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    ACTIVE = "active"
    COMPLETED = "completed"


class InvitationStatus(str, enum.Enum):
    """Event invitation status"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    EXPIRED = "expired"


class LiveHackingEvent(Base):
    """Live hacking event model"""
    __tablename__ = "live_hacking_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, name="event_id")
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(SQLEnum(EventStatus), nullable=False, default=EventStatus.DRAFT)
    
    # Time window
    start_time = Column(TIMESTAMP, nullable=False)
    end_time = Column(TIMESTAMP, nullable=False)
    
    # Configuration
    max_participants = Column(Integer, nullable=True)
    prize_pool = Column(DECIMAL(15, 2), nullable=True)
    
    # Scope definition
    scope_description = Column(Text, nullable=True)
    target_assets = Column(Text, nullable=True)  # JSON array of URLs/IPs
    
    # Reward policy
    reward_policy = Column(Text, nullable=True)
    
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    participations = relationship("EventParticipation", back_populates="event", cascade="all, delete-orphan")
    invitations = relationship("EventInvitation", back_populates="event", cascade="all, delete-orphan")
    metrics = relationship("EventMetrics", back_populates="event", uselist=False, cascade="all, delete-orphan")
    submissions = relationship("VulnerabilityReport", back_populates="live_event")


class EventParticipation(Base):
    """Event participation model"""
    __tablename__ = "event_participations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, name="participation_id")
    event_id = Column(UUID(as_uuid=True), ForeignKey("live_hacking_events.event_id"), nullable=False)
    researcher_id = Column(UUID(as_uuid=True), ForeignKey("researchers.id"), nullable=False)
    
    status = Column(SQLEnum(ParticipationStatus), nullable=False, default=ParticipationStatus.INVITED)
    
    # Performance metrics
    score = Column(Integer, default=0)
    rank = Column(Integer, nullable=True)
    submissions_count = Column(Integer, default=0)
    valid_submissions_count = Column(Integer, default=0)
    prize_amount = Column(DECIMAL(15, 2), nullable=True)
    
    joined_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    completed_at = Column(TIMESTAMP, nullable=True)
    
    # Relationships
    event = relationship("LiveHackingEvent", back_populates="participations")


class EventInvitation(Base):
    """Event invitation model"""
    __tablename__ = "event_invitations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, name="invitation_id")
    event_id = Column(UUID(as_uuid=True), ForeignKey("live_hacking_events.event_id"), nullable=False)
    researcher_id = Column(UUID(as_uuid=True), ForeignKey("researchers.id"), nullable=False)
    
    status = Column(SQLEnum(InvitationStatus), nullable=False, default=InvitationStatus.PENDING)
    
    invited_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    responded_at = Column(TIMESTAMP, nullable=True)
    expires_at = Column(TIMESTAMP, nullable=True)
    
    # Relationships
    event = relationship("LiveHackingEvent", back_populates="invitations")


class EventMetrics(Base):
    """Event metrics model for real-time dashboard"""
    __tablename__ = "event_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, name="metrics_id")
    event_id = Column(UUID(as_uuid=True), ForeignKey("live_hacking_events.event_id"), unique=True, nullable=False)
    
    # Participation metrics
    total_invited = Column(Integer, default=0)
    total_accepted = Column(Integer, default=0)
    total_active = Column(Integer, default=0)
    
    # Submission metrics
    total_submissions = Column(Integer, default=0)
    valid_submissions = Column(Integer, default=0)
    invalid_submissions = Column(Integer, default=0)
    duplicate_submissions = Column(Integer, default=0)
    
    # Severity breakdown
    critical_bugs = Column(Integer, default=0)
    high_bugs = Column(Integer, default=0)
    medium_bugs = Column(Integer, default=0)
    low_bugs = Column(Integer, default=0)
    info_bugs = Column(Integer, default=0)
    
    # Reward metrics
    total_rewards_paid = Column(DECIMAL(15, 2), default=0)
    average_reward = Column(DECIMAL(15, 2), default=0)
    
    # Performance metrics
    participation_rate = Column(DECIMAL(5, 2), default=0)  # Percentage
    average_time_to_first_bug = Column(Integer, nullable=True)  # Minutes
    
    last_updated = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    event = relationship("LiveHackingEvent", back_populates="metrics")
