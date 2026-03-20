"""
AI Red Teaming Domain Models
Implements FREQ-45, FREQ-46, FREQ-47, FREQ-48: AI Security Testing
"""
from sqlalchemy import Column, String, Integer, Text, ForeignKey, TIMESTAMP, Enum as SQLEnum, DECIMAL, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from backend.src.core.database import Base


class AIModelType(str, enum.Enum):
    """AI model types for testing"""
    LLM = "llm"
    ML_MODEL = "ml_model"
    AI_AGENT = "ai_agent"
    CHATBOT = "chatbot"
    RECOMMENDATION_SYSTEM = "recommendation_system"
    COMPUTER_VISION = "computer_vision"


class EngagementStatus(str, enum.Enum):
    """AI Red Teaming engagement status"""
    DRAFT = "draft"
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class AIAttackType(str, enum.Enum):
    """AI-specific attack types"""
    PROMPT_INJECTION = "prompt_injection"
    JAILBREAK = "jailbreak"
    DATA_LEAKAGE = "data_leakage"
    MODEL_EXTRACTION = "model_extraction"
    ADVERSARIAL_INPUT = "adversarial_input"
    BIAS_EXPLOITATION = "bias_exploitation"
    HALLUCINATION_TRIGGER = "hallucination_trigger"
    CONTEXT_MANIPULATION = "context_manipulation"
    TRAINING_DATA_POISONING = "training_data_poisoning"
    MODEL_INVERSION = "model_inversion"


class AIClassification(str, enum.Enum):
    """AI vulnerability classification categories"""
    SECURITY = "security"
    SAFETY = "safety"
    TRUST = "trust"
    PRIVACY = "privacy"
    FAIRNESS = "fairness"
    RELIABILITY = "reliability"


class ReportStatus(str, enum.Enum):
    """AI vulnerability report status"""
    NEW = "new"
    TRIAGED = "triaged"
    VALIDATED = "validated"
    INVALID = "invalid"
    DUPLICATE = "duplicate"
    RESOLVED = "resolved"


class AIRedTeamingEngagement(Base):
    """AI Red Teaming engagement model"""
    __tablename__ = "ai_red_teaming_engagements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, name="engagement_id")
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    
    # Engagement details
    name = Column(String(255), nullable=False)
    target_ai_system = Column(String(255), nullable=False)
    model_type = Column(SQLEnum(AIModelType), nullable=False)
    
    # Scope definition (FREQ-46)
    testing_environment = Column(String(500), nullable=False)
    ethical_guidelines = Column(Text, nullable=False)
    scope_description = Column(Text, nullable=True)
    allowed_attack_types = Column(JSON, nullable=True)  # Array of allowed attack types
    
    # Status and timeline
    status = Column(SQLEnum(EngagementStatus), nullable=False, default=EngagementStatus.DRAFT)
    start_date = Column(TIMESTAMP, nullable=True)
    end_date = Column(TIMESTAMP, nullable=True)
    
    # Expert assignment
    assigned_experts = Column(JSON, nullable=True)  # Array of researcher UUIDs
    
    # Metrics
    total_findings = Column(Integer, default=0)
    critical_findings = Column(Integer, default=0)
    high_findings = Column(Integer, default=0)
    medium_findings = Column(Integer, default=0)
    low_findings = Column(Integer, default=0)
    
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    testing_env = relationship("AITestingEnvironment", back_populates="engagement", uselist=False, cascade="all, delete-orphan")
    vulnerability_reports = relationship("AIVulnerabilityReport", back_populates="engagement", cascade="all, delete-orphan")


class AITestingEnvironment(Base):
    """AI testing environment configuration"""
    __tablename__ = "ai_testing_environments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, name="environment_id")
    engagement_id = Column(UUID(as_uuid=True), ForeignKey("ai_red_teaming_engagements.engagement_id"), unique=True, nullable=False)
    
    # Environment configuration
    model_type = Column(String(100), nullable=False)
    sandbox_url = Column(String(500), nullable=False)
    api_endpoint = Column(String(500), nullable=False)
    access_token = Column(String(500), nullable=False)  # Should be encrypted
    
    # Access controls
    access_controls = Column(JSON, nullable=False)
    rate_limits = Column(JSON, nullable=True)
    is_isolated = Column(Boolean, default=True)
    
    # Monitoring
    monitoring_enabled = Column(Boolean, default=True)
    log_all_interactions = Column(Boolean, default=True)
    
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    
    # Relationships
    engagement = relationship("AIRedTeamingEngagement", back_populates="testing_env")


class AIVulnerabilityReport(Base):
    """AI-specific vulnerability report model (FREQ-47)"""
    __tablename__ = "ai_vulnerability_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, name="report_id")
    engagement_id = Column(UUID(as_uuid=True), ForeignKey("ai_red_teaming_engagements.engagement_id"), nullable=False)
    researcher_id = Column(UUID(as_uuid=True), ForeignKey("researchers.id"), nullable=False)
    
    # Report details
    title = Column(String(255), nullable=False)
    
    # AI-specific fields (FREQ-47)
    input_prompt = Column(Text, nullable=False)
    model_response = Column(Text, nullable=False)
    attack_type = Column(SQLEnum(AIAttackType), nullable=False)
    
    # Classification
    classification = Column(SQLEnum(AIClassification), nullable=True)
    severity = Column(String(20), nullable=False)  # critical, high, medium, low
    
    # Detailed information
    impact = Column(Text, nullable=False)
    reproduction_steps = Column(Text, nullable=False)
    mitigation_recommendation = Column(Text, nullable=True)
    
    # Additional context
    model_version = Column(String(100), nullable=True)
    environment_details = Column(JSON, nullable=True)
    
    # Status
    status = Column(SQLEnum(ReportStatus), nullable=False, default=ReportStatus.NEW)
    
    # Timestamps
    submitted_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    validated_at = Column(TIMESTAMP, nullable=True)
    
    # Relationships
    engagement = relationship("AIRedTeamingEngagement", back_populates="vulnerability_reports")
    classification_detail = relationship("AIFindingClassification", back_populates="report", uselist=False, cascade="all, delete-orphan")


class AIFindingClassification(Base):
    """AI finding classification for triage (FREQ-48)"""
    __tablename__ = "ai_finding_classifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, name="classification_id")
    report_id = Column(UUID(as_uuid=True), ForeignKey("ai_vulnerability_reports.report_id"), unique=True, nullable=False)
    
    # Classification
    primary_category = Column(SQLEnum(AIClassification), nullable=False)
    secondary_categories = Column(JSON, nullable=True)  # Array of additional categories
    
    # Risk assessment
    risk_score = Column(DECIMAL(5, 2), nullable=True)  # 0-100
    confidence_level = Column(DECIMAL(5, 2), nullable=True)  # 0-100
    
    # Triage information
    classified_by = Column(UUID(as_uuid=True), ForeignKey("staff.id"), nullable=True)
    classified_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    justification = Column(Text, nullable=False)
    
    # Additional metadata
    affected_components = Column(JSON, nullable=True)
    remediation_priority = Column(String(20), nullable=True)
    
    # Relationships
    report = relationship("AIVulnerabilityReport", back_populates="classification_detail")


class AISecurityReport(Base):
    """AI security summary report (FREQ-48)"""
    __tablename__ = "ai_security_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, name="report_id")
    engagement_id = Column(UUID(as_uuid=True), ForeignKey("ai_red_teaming_engagements.engagement_id"), nullable=False)
    
    # Report metadata
    report_title = Column(String(255), nullable=False)
    generated_by = Column(UUID(as_uuid=True), ForeignKey("staff.id"), nullable=True)
    
    # Summary statistics
    total_findings = Column(Integer, default=0)
    security_findings = Column(Integer, default=0)
    safety_findings = Column(Integer, default=0)
    trust_findings = Column(Integer, default=0)
    privacy_findings = Column(Integer, default=0)
    fairness_findings = Column(Integer, default=0)
    
    # Severity breakdown
    critical_count = Column(Integer, default=0)
    high_count = Column(Integer, default=0)
    medium_count = Column(Integer, default=0)
    low_count = Column(Integer, default=0)
    
    # Report content
    executive_summary = Column(Text, nullable=True)
    key_findings = Column(JSON, nullable=True)
    recommendations = Column(Text, nullable=True)
    
    # Timestamps
    generated_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    
    # Report file
    report_file_url = Column(String(500), nullable=True)
