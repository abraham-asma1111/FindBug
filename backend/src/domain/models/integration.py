"""
SSDLC Integration Domain Models
Implements FREQ-42: Jira and GitHub Integration
"""
from sqlalchemy import Column, String, Integer, Text, ForeignKey, TIMESTAMP, Boolean, Enum as SQLEnum, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from backend.src.core.database import Base


class IntegrationType(str, enum.Enum):
    """Integration types"""
    JIRA = "jira"
    GITHUB = "github"
    GITLAB = "gitlab"
    AZURE_DEVOPS = "azure_devops"


class IntegrationStatus(str, enum.Enum):
    """Integration status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    PENDING = "pending"


class SyncAction(str, enum.Enum):
    """Sync actions"""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    SYNC = "sync"


class SyncStatus(str, enum.Enum):
    """Sync status"""
    SUCCESS = "success"
    FAILED = "failed"
    PENDING = "pending"
    CONFLICT = "conflict"


class TransformationType(str, enum.Enum):
    """Field transformation types"""
    DIRECT = "direct"
    MAPPING = "mapping"
    FUNCTION = "function"
    TEMPLATE = "template"


class ExternalIntegration(Base):
    """External integration model"""
    __tablename__ = "external_integrations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    
    type = Column(SQLEnum(IntegrationType), nullable=False)
    status = Column(SQLEnum(IntegrationStatus), nullable=False, default=IntegrationStatus.PENDING)
    
    config = Column(JSON, nullable=False)  # API keys, URLs, project IDs, etc.
    last_sync_at = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    
    # Relationships
    sync_logs = relationship("SyncLog", back_populates="integration", cascade="all, delete-orphan")
    field_mappings = relationship("IntegrationFieldMapping", back_populates="integration", cascade="all, delete-orphan")
    webhook_events = relationship("IntegrationWebhookEvent", back_populates="integration", cascade="all, delete-orphan")


class SyncLog(Base):
    """Sync log model"""
    __tablename__ = "sync_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    integration_id = Column(UUID(as_uuid=True), ForeignKey("external_integrations.id"), nullable=False)
    report_id = Column(UUID(as_uuid=True), ForeignKey("vulnerability_reports.id"), nullable=True)
    
    action = Column(SQLEnum(SyncAction), nullable=False)
    status = Column(SQLEnum(SyncStatus), nullable=False)
    
    error_message = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    
    # Relationships
    integration = relationship("ExternalIntegration", back_populates="sync_logs")


class IntegrationFieldMapping(Base):
    """Integration field mapping model"""
    __tablename__ = "integration_field_mappings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    integration_id = Column(UUID(as_uuid=True), ForeignKey("external_integrations.id"), nullable=False)
    
    source_field = Column(String(100), nullable=False)
    target_field = Column(String(100), nullable=False)
    transformation = Column(SQLEnum(TransformationType), nullable=False, default=TransformationType.DIRECT)
    
    is_required = Column(Boolean, default=False)
    default_value = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    
    # Relationships
    integration = relationship("ExternalIntegration", back_populates="field_mappings")


class IntegrationWebhookEvent(Base):
    """Integration webhook event model"""
    __tablename__ = "integration_webhook_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    integration_id = Column(UUID(as_uuid=True), ForeignKey("external_integrations.id"), nullable=False)
    
    event_type = Column(String(100), nullable=False)
    payload = Column(JSON, nullable=False)
    headers = Column(JSON, nullable=True)
    signature = Column(String(500), nullable=True)
    
    is_verified = Column(Boolean, default=False)
    processed = Column(Boolean, default=False)
    processed_at = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    
    # Relationships
    integration = relationship("ExternalIntegration", back_populates="webhook_events")


class IntegrationTemplate(Base):
    """Integration template model"""
    __tablename__ = "integration_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    name = Column(String(100), nullable=False)
    integration_type = Column(SQLEnum(IntegrationType), nullable=False)
    description = Column(Text, nullable=True)
    
    default_config = Column(JSON, nullable=False)
    field_mappings = Column(JSON, nullable=False)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
