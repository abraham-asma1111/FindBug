"""
Pending Registration Model - Store registration data before email verification
"""
from datetime import datetime, timedelta
from sqlalchemy import Column, String, DateTime, Boolean, Text, Enum
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum

from src.core.database import Base


class RegistrationType(str, enum.Enum):
    """Registration type enum"""
    RESEARCHER = "researcher"
    ORGANIZATION = "organization"


class PendingRegistration(Base):
    """
    Pending Registration - Store registration data before email verification
    
    Flow:
    1. User submits registration form
    2. Data stored in pending_registrations table
    3. Verification email sent with OTP/token
    4. User verifies email
    5. User account created from pending data
    6. Pending registration deleted
    """
    __tablename__ = "pending_registrations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Basic info
    email = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    registration_type = Column(Enum(RegistrationType), nullable=False)
    
    # Personal info
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    
    # Organization-specific fields (nullable for researchers)
    company_name = Column(String(200), nullable=True)
    phone_number = Column(String(20), nullable=True)
    country = Column(String(100), nullable=True)
    
    # Verification
    verification_token = Column(String(255), nullable=False, index=True)
    verification_otp = Column(String(10), nullable=True)  # 6-digit OTP
    otp_expires_at = Column(DateTime, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)  # 24 hours from creation
    verified_at = Column(DateTime, nullable=True)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Request info
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.expires_at:
            self.expires_at = datetime.utcnow() + timedelta(hours=24)
    
    @property
    def is_expired(self) -> bool:
        """Check if registration has expired"""
        return datetime.utcnow() > self.expires_at
    
    @property
    def otp_is_expired(self) -> bool:
        """Check if OTP has expired"""
        if not self.otp_expires_at:
            return True
        return datetime.utcnow() > self.otp_expires_at
    
    def __repr__(self):
        return f"<PendingRegistration(email='{self.email}', type='{self.registration_type}')>"