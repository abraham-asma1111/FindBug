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
    """User roles enum (aligned with RAD Table 1 / FREQ-01)."""
    RESEARCHER = "researcher"
    ORGANIZATION = "organization"
    STAFF = "staff"  # generic platform staff
    TRIAGE_SPECIALIST = "triage_specialist"
    FINANCE_OFFICER = "finance_officer"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class User(Base):
    """
    User model - Core authentication entity
    
    Supports multiple roles including triage specialist and finance officer (RAD)
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
    last_login_ip = Column(String(45), nullable=True)
    last_login_device = Column(String(255), nullable=True)
    
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
    password_reset_token = Column(String(255), nullable=True)
    password_reset_token_expires = Column(DateTime, nullable=True)
    
    # Refresh Token
    refresh_token = Column(String(500), nullable=True)
    refresh_token_expires = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)
    
    # Relationships
    researcher = relationship("Researcher", back_populates="user", uselist=False)
    organization = relationship("Organization", back_populates="user", uselist=False)
    staff = relationship("Staff", back_populates="user", uselist=False)
    triage_specialist = relationship("TriageSpecialist", back_populates="user", uselist=False)
    administrator = relationship("Administrator", back_populates="user", uselist=False)
    financial_officer = relationship("FinancialOfficer", back_populates="user", uselist=False)
    kyc_verifications = relationship("KYCVerification", foreign_keys="KYCVerification.user_id",
                                     back_populates="user", cascade="all, delete-orphan")
    security_events = relationship("SecurityEvent", back_populates="user", cascade="all, delete-orphan")
    login_history = relationship("LoginHistory", back_populates="user", cascade="all, delete-orphan")
    data_exports = relationship("DataExport", back_populates="user", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="user")
    payment_methods = relationship("PaymentMethod", back_populates="user", cascade="all, delete-orphan")
