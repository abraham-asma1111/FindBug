"""
Researcher Model - Security researcher profile
Based on Extended ERD + Bugcrowd 2026 enhancements
"""
from sqlalchemy import Column, String, Integer, Text, ForeignKey, DateTime, DECIMAL, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from src.core.database import Base


class Researcher(Base):
    """
    Researcher model - Security researcher profile
    
    Extended ERD (10 columns) + Bugcrowd 2026 enhancements
    """
    __tablename__ = "researchers"
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign Key to User
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)
    
    # Bugcrowd 2026 Identity Fields
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    username = Column(String(50), nullable=True, unique=True)
    ninja_email = Column(String(255), nullable=True, unique=True)
    
    # Extended ERD Profile Information
    bio = Column(Text, nullable=True)
    website = Column(String(500), nullable=True)
    github = Column(String(255), nullable=True)
    twitter = Column(String(255), nullable=True)
    
    # Extended ERD Reputation System
    reputation_score = Column(DECIMAL(5, 2), default=0)
    rank = Column(Integer, nullable=True)
    total_earnings = Column(DECIMAL(15, 2), default=0)
    
    # Report Statistics
    total_reports = Column(Integer, default=0)
    verified_reports = Column(Integer, default=0)
    
    # Account Status
    is_active = Column(Boolean, default=True)
    
    # Bugcrowd 2026 Professional Fields
    linkedin = Column(String(255), nullable=True)
    skills = Column(Text, nullable=True)
    kyc_status = Column(String(20), default="pending")
    kyc_document_url = Column(String(500), nullable=True)
    
    # Extended ERD Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="researcher")
    program_invitations = relationship("ProgramInvitation", back_populates="researcher", cascade="all, delete-orphan")
    participations = relationship("ProgramParticipation", back_populates="researcher", cascade="all, delete-orphan")
    payout_requests = relationship("PayoutRequest", back_populates="researcher", cascade="all, delete-orphan")
