"""
Staff Model - Platform staff profile
"""
from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from src.core.database import Base


class Staff(Base):
    """
    Staff model - Platform staff profile
    
    Stores staff-specific information
    """
    __tablename__ = "staff"
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign Key to User
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)
    
    # Staff Information
    full_name = Column(String(255), nullable=False)
    department = Column(String(100), nullable=True)
    position = Column(String(100), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="staff")
