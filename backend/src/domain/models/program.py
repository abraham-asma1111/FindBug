"""Bounty Program domain models."""
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from uuid import UUID, uuid4

from sqlalchemy import (
    Column, String, Text, DateTime, Numeric, Integer, Boolean,
    ForeignKey, func
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship

from src.core.database import Base


class BountyProgram(Base):
    """Bounty Program model."""
    
    __tablename__ = "bounty_programs"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    organization_id = Column(PGUUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    type = Column(String(20), nullable=False)  # bounty, vdp
    status = Column(String(20), nullable=False, server_default="draft")  # draft, private, public, paused, closed
    visibility = Column(String(20), nullable=False, server_default="private")  # private, public
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    budget = Column(Numeric(15, 2), nullable=True)
    policy = Column(Text, nullable=True)
    rules_of_engagement = Column(Text, nullable=True)
    safe_harbor = Column(Text, nullable=True)
    response_sla_hours = Column(Integer, nullable=True, server_default="72")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="programs")
    scopes = relationship("ProgramScope", back_populates="program", cascade="all, delete-orphan")
    reward_tiers = relationship("RewardTier", back_populates="program", cascade="all, delete-orphan")
    invitations = relationship("ProgramInvitation", back_populates="program", cascade="all, delete-orphan")


class ProgramScope(Base):
    """Program Scope model - defines what assets are in/out of scope."""
    
    __tablename__ = "program_scopes"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    program_id = Column(PGUUID(as_uuid=True), ForeignKey("bounty_programs.id", ondelete="CASCADE"), nullable=False)
    asset_type = Column(String(50), nullable=False)  # domain, api, mobile_app, web_app, other
    asset_identifier = Column(String(500), nullable=False)  # example.com, api.example.com, etc.
    is_in_scope = Column(Boolean, nullable=False, server_default="true")
    description = Column(Text, nullable=False)
    max_severity = Column(String(20), nullable=False)  # critical, high, medium, low
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    program = relationship("BountyProgram", back_populates="scopes")


class RewardTier(Base):
    """Reward Tier model - defines payout amounts by severity."""
    
    __tablename__ = "reward_tiers"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    program_id = Column(PGUUID(as_uuid=True), ForeignKey("bounty_programs.id", ondelete="CASCADE"), nullable=False)
    severity = Column(String(20), nullable=False)  # critical, high, medium, low
    min_amount = Column(Numeric(15, 2), nullable=False)
    max_amount = Column(Numeric(15, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    program = relationship("BountyProgram", back_populates="reward_tiers")


class ProgramInvitation(Base):
    """Program Invitation model - for private program invites."""
    
    __tablename__ = "program_invitations"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    program_id = Column(PGUUID(as_uuid=True), ForeignKey("bounty_programs.id", ondelete="CASCADE"), nullable=False)
    researcher_id = Column(PGUUID(as_uuid=True), ForeignKey("researchers.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(20), nullable=False, server_default="pending")  # pending, accepted, declined, expired
    invited_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    message = Column(Text, nullable=False)
    invited_at = Column(DateTime(timezone=True), server_default=func.now())
    responded_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    program = relationship("BountyProgram", back_populates="invitations")
    researcher = relationship("Researcher", back_populates="program_invitations")
    inviter = relationship("User", foreign_keys=[invited_by])


class ProgramParticipation(Base):
    """Program Participation model - tracks researcher participation in programs."""
    
    __tablename__ = "program_participations"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    program_id = Column(PGUUID(as_uuid=True), ForeignKey("bounty_programs.id", ondelete="CASCADE"), nullable=False)
    researcher_id = Column(PGUUID(as_uuid=True), ForeignKey("researchers.id", ondelete="CASCADE"), nullable=False)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String(20), nullable=False, server_default="active")  # active, left
    left_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    program = relationship("BountyProgram")
    researcher = relationship("Researcher")
