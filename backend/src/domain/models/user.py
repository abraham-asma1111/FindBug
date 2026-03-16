"""
User Model - Core user entity for all roles
"""
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Enum as SQLEnum, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from src.core.database import Base


class UserRole(str, enum.Enum):
    """User roles enum"""
    RESEARCHER = "researcher"
    ORGANIZATION = "organization"
    STAFF = "staff"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class User(Base):
    """
    User model - Core authentication entity
    
    Supports multiple roles: researcher, organization, staff, admin
    Includes security features: MFA, account lockout, failed login tracking
    """
    __tablename__ = "users"
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Authentication
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False)
    
    # Account Status
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    is_locked = Column(Boolean, default=False)
    locked_until = Column(DateTime, nullable=True)
    
    # Security Tracking
    failed_login_attempts = Column(Integer, default=0)
    last_login_at = Column(DateTime, nullable=True)
    
    # MFA (Multi-Factor Authentication)
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String(255), nullable=True)
    mfa_backup_codes = Column(Text, nullable=True)
    
    # Email Verification
    email_verification_token = Column(String(255), nullable=True)
    email_verification_token_expires = Column(DateTime, nullable=True)
    email_verified_at = Column(DateTime, nullable=True)
    
    # Password Management
    password_changed_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)
    
    # Relationships
    researcher = relationship("Researcher", back_populates="user", uselist=False)
    organization = relationship("Organization", back_populates="user", uselist=False)
    staff = relationship("Staff", back_populates="user", uselist=False)
