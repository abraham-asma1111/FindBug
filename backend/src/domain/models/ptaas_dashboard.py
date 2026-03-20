"""
PTaaS Dashboard Models - FREQ-34
Real-time progress tracking for PTaaS engagements
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from backend.src.core.database import Base


class PTaaSTestingPhase(Base):
    """Testing Phase model - FREQ-34"""
    __tablename__ = "ptaas_testing_phases"

    id = Column(Integer, primary_key=True, index=True)
    engagement_id = Column(Integer, ForeignKey("ptaas_engagements.id"), nullable=False)
    
    phase_name = Column(String(100), nullable=False)
    phase_order = Column(Integer, nullable=False)
    description = Column(Text)
    
    status = Column(String(50), default="NOT_STARTED")  # NOT_STARTED, IN_PROGRESS, COMPLETED, BLOCKED
    progress_percentage = Column(Integer, default=0)
    
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    estimated_completion = Column(DateTime)
    
    assigned_to = Column(Integer, ForeignKey("users.id"))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    engagement = relationship("PTaaSEngagement", backref="testing_phases")
    checklist_items = relationship("PTaaSChecklistItem", back_populates="phase", cascade="all, delete-orphan")


class PTaaSChecklistItem(Base):
    """Methodology Checklist Item - FREQ-34"""
    __tablename__ = "ptaas_checklist_items"

    id = Column(Integer, primary_key=True, index=True)
    phase_id = Column(Integer, ForeignKey("ptaas_testing_phases.id"), nullable=False)
    engagement_id = Column(Integer, ForeignKey("ptaas_engagements.id"), nullable=False)
    
    item_name = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(100))  # reconnaissance, scanning, exploitation, etc.
    
    is_completed = Column(Boolean, default=False)
    is_required = Column(Boolean, default=True)
    
    completed_by = Column(Integer, ForeignKey("users.id"))
    completed_at = Column(DateTime)
    notes = Column(Text)
    
    evidence_url = Column(String(500))  # Link to evidence/documentation
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    phase = relationship("PTaaSTestingPhase", back_populates="checklist_items")


class PTaaSCollaborationUpdate(Base):
    """Collaboration Update - FREQ-34"""
    __tablename__ = "ptaas_collaboration_updates"

    id = Column(Integer, primary_key=True, index=True)
    engagement_id = Column(Integer, ForeignKey("ptaas_engagements.id"), nullable=False)
    
    update_type = Column(String(50), nullable=False)  # MESSAGE, FINDING, PHASE_CHANGE, MILESTONE, QUESTION
    title = Column(String(255))
    content = Column(Text, nullable=False)
    
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Mentions and visibility
    mentioned_users = Column(JSON)  # List of user IDs mentioned
    is_pinned = Column(Boolean, default=False)
    priority = Column(String(20), default="NORMAL")  # LOW, NORMAL, HIGH, URGENT
    
    # Related entities
    related_finding_id = Column(Integer, ForeignKey("ptaas_findings.id"))
    related_phase_id = Column(Integer, ForeignKey("ptaas_testing_phases.id"))
    
    # Attachments
    attachments = Column(JSON)  # List of file URLs
    
    # Relationships
    engagement = relationship("PTaaSEngagement", backref="collaboration_updates")


class PTaaSMilestone(Base):
    """Milestone tracking - FREQ-34"""
    __tablename__ = "ptaas_milestones"

    id = Column(Integer, primary_key=True, index=True)
    engagement_id = Column(Integer, ForeignKey("ptaas_engagements.id"), nullable=False)
    
    milestone_name = Column(String(255), nullable=False)
    description = Column(Text)
    
    target_date = Column(DateTime, nullable=False)
    completed_date = Column(DateTime)
    
    status = Column(String(50), default="PENDING")  # PENDING, IN_PROGRESS, COMPLETED, MISSED
    
    deliverables = Column(JSON)  # List of expected deliverables
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    engagement = relationship("PTaaSEngagement", backref="milestones")
