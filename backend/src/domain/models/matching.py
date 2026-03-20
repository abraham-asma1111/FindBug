"""BountyMatch (Researcher Matching) domain models - FREQ-16, FREQ-32, FREQ-33, FREQ-39, FREQ-40."""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import (
    Column, String, Text, DateTime, Numeric, Integer, Boolean,
    ForeignKey, func, Index, JSON
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import relationship

from src.core.database import Base


class SkillTag(Base):
    """Skill Tag model - Skill taxonomy."""
    
    __tablename__ = "skill_tags"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    parent_tag_id = Column(PGUUID(as_uuid=True), ForeignKey("skill_tags.id"), nullable=True)
    
    name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)  # web, mobile, api, cloud, etc.
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, server_default="true")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    parent_tag = relationship("SkillTag", remote_side=[id], backref="child_tags")
    researcher_skills = relationship("ResearcherSkill", back_populates="skill_tag")
    
    __table_args__ = (
        Index('ix_skill_tags_name', 'name'),
        Index('ix_skill_tags_category', 'category'),
    )


class ResearcherProfile(Base):
    """Researcher Profile model - Extended profile for matching."""
    
    __tablename__ = "researcher_profiles"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    researcher_id = Column(PGUUID(as_uuid=True), ForeignKey("researchers.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    # Skills and specializations
    skills = Column(JSONB, nullable=True)  # Array of skill names
    specializations = Column(JSONB, nullable=True)  # Array of specialization areas
    
    # Experience
    experience_years = Column(Integer, nullable=False, server_default="0")
    
    # Availability
    timezone = Column(String(50), nullable=True)
    availability_hours = Column(Integer, nullable=True)  # Hours per week
    current_workload = Column(Integer, nullable=False, server_default="0")  # Current active engagements
    
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    researcher = relationship("Researcher", backref="profile")
    skills_detail = relationship("ResearcherSkill", back_populates="researcher_profile")
    
    __table_args__ = (
        Index('ix_researcher_profiles_researcher_id', 'researcher_id'),
    )


class ResearcherSkill(Base):
    """Researcher Skill model - Detailed skill mapping."""
    
    __tablename__ = "researcher_skills"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    researcher_id = Column(PGUUID(as_uuid=True), ForeignKey("researchers.id", ondelete="CASCADE"), nullable=False)
    tag_id = Column(PGUUID(as_uuid=True), ForeignKey("skill_tags.id"), nullable=False)
    
    level = Column(String(20), nullable=False)  # beginner, intermediate, advanced, expert
    years_experience = Column(Integer, nullable=False, server_default="0")
    verified = Column(Boolean, nullable=False, server_default="false")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    researcher_profile = relationship("ResearcherProfile", back_populates="skills_detail")
    skill_tag = relationship("SkillTag", back_populates="researcher_skills")
    
    __table_args__ = (
        Index('ix_researcher_skills_researcher_id', 'researcher_id'),
        Index('ix_researcher_skills_tag_id', 'tag_id'),
    )


class MatchingAlgorithm(Base):
    """Matching Algorithm model - Algorithm configuration."""
    
    __tablename__ = "matching_algorithms"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    
    version = Column(String(20), nullable=False, unique=True)
    weights = Column(JSONB, nullable=False)  # Weights for different factors
    parameters = Column(JSONB, nullable=False)  # Algorithm parameters
    is_active = Column(Boolean, nullable=False, server_default="false")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        Index('ix_matching_algorithms_version', 'version'),
        Index('ix_matching_algorithms_is_active', 'is_active'),
    )


class MatchingRequest(Base):
    """Matching Request model - Request for researcher matching."""
    
    __tablename__ = "matching_requests"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    engagement_id = Column(PGUUID(as_uuid=True), nullable=True)  # Generic engagement ID
    organization_id = Column(PGUUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    
    engagement_type = Column(String(50), nullable=False)  # bug_bounty, ptaas, code_review, ai_red_teaming
    criteria = Column(JSONB, nullable=False)  # Matching criteria
    required_skills = Column(JSONB, nullable=True)  # Required skills
    status = Column(String(20), nullable=False, server_default="pending")  # pending, processing, completed, failed
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    organization = relationship("Organization")
    match_results = relationship("MatchResult", back_populates="request", cascade="all, delete-orphan")
    invitations = relationship("MatchingInvitation", back_populates="request", cascade="all, delete-orphan")
    metrics = relationship("MatchingMetrics", back_populates="request", uselist=False, cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('ix_matching_requests_organization_id', 'organization_id'),
        Index('ix_matching_requests_status', 'status'),
        Index('ix_matching_requests_engagement_type', 'engagement_type'),
    )


class MatchResult(Base):
    """Match Result model - Match scores for researchers."""
    
    __tablename__ = "match_results"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    request_id = Column(PGUUID(as_uuid=True), ForeignKey("matching_requests.id", ondelete="CASCADE"), nullable=False)
    researcher_id = Column(PGUUID(as_uuid=True), ForeignKey("researchers.id"), nullable=False)
    
    match_score = Column(Numeric(5, 2), nullable=False)  # Overall match score (0-100)
    skill_score = Column(Numeric(5, 2), nullable=False)  # Skill match score (0-100)
    reputation_score = Column(Numeric(5, 2), nullable=False)  # Reputation score (0-100)
    rank = Column(Integer, nullable=False)  # Rank in results
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    request = relationship("MatchingRequest", back_populates="match_results")
    researcher = relationship("Researcher")
    
    __table_args__ = (
        Index('ix_match_results_request_id', 'request_id'),
        Index('ix_match_results_researcher_id', 'researcher_id'),
        Index('ix_match_results_match_score', 'match_score'),
    )


class MatchingInvitation(Base):
    """Matching Invitation model - Invitations sent to matched researchers."""
    
    __tablename__ = "matching_invitations"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    request_id = Column(PGUUID(as_uuid=True), ForeignKey("matching_requests.id", ondelete="CASCADE"), nullable=False)
    researcher_id = Column(PGUUID(as_uuid=True), ForeignKey("researchers.id"), nullable=False)
    engagement_id = Column(PGUUID(as_uuid=True), nullable=True)  # Specific engagement ID
    
    match_score = Column(Numeric(5, 2), nullable=False)
    status = Column(String(20), nullable=False, server_default="pending")  # pending, viewed, accepted, declined, expired
    message = Column(Text, nullable=True)
    
    expires_at = Column(DateTime(timezone=True), nullable=False)
    sent_at = Column(DateTime(timezone=True), server_default=func.now())
    viewed_at = Column(DateTime(timezone=True), nullable=True)
    responded_at = Column(DateTime(timezone=True), nullable=True)
    response_note = Column(Text, nullable=True)
    
    # Relationships
    request = relationship("MatchingRequest", back_populates="invitations")
    researcher = relationship("Researcher")
    
    __table_args__ = (
        Index('ix_matching_invitations_request_id', 'request_id'),
        Index('ix_matching_invitations_researcher_id', 'researcher_id'),
        Index('ix_matching_invitations_status', 'status'),
    )


class MatchingFeedback(Base):
    """Matching Feedback model - Feedback on matches."""
    
    __tablename__ = "matching_feedback"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    request_id = Column(PGUUID(as_uuid=True), ForeignKey("matching_requests.id"), nullable=False)
    researcher_id = Column(PGUUID(as_uuid=True), ForeignKey("researchers.id"), nullable=False)
    organization_id = Column(PGUUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    
    rating = Column(Integer, nullable=False)  # Overall rating (1-5)
    quality_score = Column(Integer, nullable=False)  # Quality score (1-5)
    communication_score = Column(Integer, nullable=False)  # Communication score (1-5)
    timeliness_score = Column(Integer, nullable=False)  # Timeliness score (1-5)
    would_work_again = Column(Boolean, nullable=False)
    comments = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    researcher = relationship("Researcher")
    organization = relationship("Organization")
    
    __table_args__ = (
        Index('ix_matching_feedback_request_id', 'request_id'),
        Index('ix_matching_feedback_researcher_id', 'researcher_id'),
        Index('ix_matching_feedback_organization_id', 'organization_id'),
    )


class MatchingMetrics(Base):
    """Matching Metrics model - Matching performance metrics."""
    
    __tablename__ = "matching_metrics"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    request_id = Column(PGUUID(as_uuid=True), ForeignKey("matching_requests.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    total_candidates = Column(Integer, nullable=False, server_default="0")
    invited_count = Column(Integer, nullable=False, server_default="0")
    accepted_count = Column(Integer, nullable=False, server_default="0")
    declined_count = Column(Integer, nullable=False, server_default="0")
    expired_count = Column(Integer, nullable=False, server_default="0")
    
    average_match_score = Column(Numeric(5, 2), nullable=True)
    average_response_time = Column(Integer, nullable=True)  # Average response time in seconds
    success_rate = Column(Numeric(5, 2), nullable=True)  # Success rate percentage
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    request = relationship("MatchingRequest", back_populates="metrics")
    
    __table_args__ = (
        Index('ix_matching_metrics_request_id', 'request_id'),
    )
