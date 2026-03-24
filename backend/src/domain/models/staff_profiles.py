"""
Staff Role Profile Models — FREQ-01
Separate profile tables for Triage Specialist, Admin, and Finance Officer roles.
Aligned with ERD: triage_specialists, administrators, financial_officers
"""
import uuid
from datetime import datetime

from sqlalchemy import Column, String, Integer, Boolean, DateTime, DECIMAL, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from src.core.database import Base


class TriageSpecialist(Base):
    """
    Triage Specialist profile — ERD: triage_specialists
    Extended profile for users with role=TRIAGE_SPECIALIST.
    """
    __tablename__ = "triage_specialists"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)

    # Specialization areas (e.g. ["web", "mobile", "api"])
    specialization = Column(JSONB, nullable=True)
    years_experience = Column(Integer, nullable=False, default=0)
    accuracy_rate = Column(DECIMAL(5, 2), nullable=True)  # % of correct triage decisions

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="triage_specialist")


class Administrator(Base):
    """
    Administrator profile — ERD: administrators
    Extended profile for users with role=ADMIN or SUPER_ADMIN.
    """
    __tablename__ = "administrators"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)

    admin_level = Column(String(20), nullable=False, default="admin")  # admin | super_admin
    permissions = Column(JSONB, nullable=True)  # granular permission overrides

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="administrator")


class FinancialOfficer(Base):
    """
    Financial Officer profile — ERD: financial_officers
    Extended profile for users with role=FINANCE_OFFICER.
    """
    __tablename__ = "financial_officers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)

    department = Column(String(100), nullable=True)
    approval_limit = Column(DECIMAL(15, 2), nullable=True)  # max bounty they can approve

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="financial_officer")
