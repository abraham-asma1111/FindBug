"""KYC Verification Model — FREQ-01"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.core.database import Base


class KYCVerification(Base):
    """KYC Verification — ERD: kyc_verifications"""
    __tablename__ = "kyc_verifications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(20), nullable=False, default="pending", index=True)
    document_type = Column(String(50), nullable=True)
    document_number = Column(String(100), nullable=True)
    document_front = Column(String(500), nullable=True)
    document_back = Column(String(500), nullable=True)
    selfie_photo = Column(String(500), nullable=True)
    verified_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    verified_at = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    user = relationship("User", foreign_keys=[user_id], back_populates="kyc_verifications")
    reviewer = relationship("User", foreign_keys=[verified_by])
