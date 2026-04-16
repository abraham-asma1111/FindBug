"""
PTaaS (Penetration Testing as a Service) Domain Models
Implements FREQ-29, FREQ-30, FREQ-31
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Numeric, Boolean, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from src.core.database import Base


class PTaaSEngagement(Base):
    """PTaaS engagement model"""
    __tablename__ = "ptaas_engagements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True)
    
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, index=True)
    
    # Scope and methodology
    scope = Column(JSON, nullable=False)
    testing_methodology = Column(String(50), nullable=False)
    custom_methodology_details = Column(Text, nullable=True)
    
    # Timeline
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    duration_days = Column(Integer, nullable=True)
    
    # Compliance
    compliance_requirements = Column(JSON, nullable=True)
    compliance_notes = Column(Text, nullable=True)
    
    # Deliverables
    deliverables = Column(JSON, nullable=False)
    
    # Pricing
    pricing_model = Column(String(50), nullable=False)
    base_price = Column(Numeric(10, 2), nullable=False)
    platform_commission_rate = Column(Numeric(5, 2), nullable=True)
    platform_commission_amount = Column(Numeric(10, 2), nullable=True)
    total_price = Column(Numeric(10, 2), nullable=True)
    
    # Subscription (for recurring engagements)
    subscription_interval = Column(String(50), nullable=True)
    subscription_start_date = Column(DateTime, nullable=True)
    subscription_end_date = Column(DateTime, nullable=True)
    
    # Team
    assigned_researchers = Column(JSON, nullable=True)
    team_size = Column(Integer, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Relationships
    findings = relationship("PTaaSFinding", back_populates="engagement", cascade="all, delete-orphan")
    deliverable_records = relationship("PTaaSDeliverable", back_populates="engagement", cascade="all, delete-orphan")
    progress_updates = relationship("PTaaSProgressUpdate", back_populates="engagement", cascade="all, delete-orphan")


class PTaaSFinding(Base):
    """PTaaS finding model"""
    __tablename__ = "ptaas_findings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    engagement_id = Column(UUID(as_uuid=True), ForeignKey("ptaas_engagements.id"), nullable=False, index=True)
    
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(String(50), nullable=False, index=True)
    cvss_score = Column(Numeric(3, 1), nullable=True)
    
    affected_component = Column(String(255), nullable=True)
    reproduction_steps = Column(Text, nullable=True)
    remediation = Column(Text, nullable=True)
    references = Column(JSON, nullable=True)
    
    status = Column(String(50), nullable=True)
    discovered_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    discovered_at = Column(DateTime, nullable=True)
    
    # Relationships
    engagement = relationship("PTaaSEngagement", back_populates="findings")


class PTaaSDeliverable(Base):
    """PTaaS deliverable model"""
    __tablename__ = "ptaas_deliverables"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    engagement_id = Column(UUID(as_uuid=True), ForeignKey("ptaas_engagements.id"), nullable=False, index=True)
    
    deliverable_type = Column(String(100), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    file_path = Column(String(500), nullable=True)
    file_url = Column(String(500), nullable=True)
    version = Column(String(50), nullable=True)
    
    submitted_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    submitted_at = Column(DateTime, nullable=True)
    
    approved = Column(Boolean, nullable=True)
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    
    # Relationships
    engagement = relationship("PTaaSEngagement", back_populates="deliverable_records")


class PTaaSProgressUpdate(Base):
    """PTaaS progress update model"""
    __tablename__ = "ptaas_progress_updates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    engagement_id = Column(UUID(as_uuid=True), ForeignKey("ptaas_engagements.id"), nullable=False, index=True)
    
    update_text = Column(Text, nullable=False)
    progress_percentage = Column(Integer, nullable=True)
    
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, nullable=True, default=datetime.utcnow)
    
    # Relationships
    engagement = relationship("PTaaSEngagement", back_populates="progress_updates")
