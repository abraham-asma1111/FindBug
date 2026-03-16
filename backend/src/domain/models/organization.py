"""
Organization Model - Company/organization profile
Based on Extended ERD + Bugcrowd 2026 enhancements
"""
from sqlalchemy import Column, String, ForeignKey, DateTime, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from src.core.database import Base


class Organization(Base):
    """
    Organization model - Company/organization profile
    
    Extended ERD (8 columns) + Bugcrowd 2026 enhancements
    """
    __tablename__ = "organizations"
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign Key to User
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)
    
    # Extended ERD Company Information
    company_name = Column(String(200), nullable=False)
    industry = Column(String(100), nullable=True)
    website = Column(String(500), nullable=True)
    subscription_type = Column(String(20), nullable=True)
    subscription_expires_at = Column(DateTime, nullable=True)
    
    # Bugcrowd 2026 Domain Verification
    domain_verified = Column(Boolean, default=False)
    domain_verification_token = Column(String(255), nullable=True)
    domain_verification_method = Column(String(20), nullable=True)
    verified_domains = Column(Text, nullable=True)
    
    # Bugcrowd 2026 Business Verification
    business_license_url = Column(String(500), nullable=True)
    tax_id = Column(String(100), nullable=True)
    verification_status = Column(String(20), default="pending")
    
    # Bugcrowd 2026 SSO Configuration
    sso_enabled = Column(Boolean, default=False)
    sso_provider = Column(String(50), nullable=True)
    sso_metadata_url = Column(String(500), nullable=True)
    
    # Extended ERD Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="organization")
