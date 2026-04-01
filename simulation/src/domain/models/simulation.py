"""
Simulation Domain Models - FREQ-23, FREQ-24, FREQ-25, FREQ-26, FREQ-27, FREQ-28
"""

from sqlalchemy import Column, String, Integer, DateTime, Text, Boolean, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from src.core.database import Base


"""
Simulation Domain Models - FREQ-23, FREQ-24, FREQ-25, FREQ-26, FREQ-27, FREQ-28
"""

from sqlalchemy import Column, String, Integer, DateTime, Text, Boolean, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from src.core.database import Base


class Simulation(Base):
    """
    Simulation sessions for practice environment
    FREQ-23: Simulation Environment
    """
    __tablename__ = "simulations"
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # User and Target
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    target_id = Column(UUID(as_uuid=True), ForeignKey("simulation_targets.id"), nullable=False)
    
    # Simulation Details
    level = Column(String(50), nullable=False)  # beginner, intermediate, advanced, expert
    status = Column(String(50), nullable=False, default="active")  # active, completed, expired, terminated
    
    # Timing
    started_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=False)
    
    # Performance Tracking
    max_hints = Column(Integer, nullable=False, default=3)
    hints_used = Column(Integer, nullable=False, default=0)
    time_spent = Column(Integer, nullable=False, default=0)  # seconds
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    target = relationship("SimulationTarget", back_populates="simulations")
    progress = relationship("SimulationProgress", back_populates="simulation", uselist=False)
    result = relationship("SimulationResult", back_populates="simulation", uselist=False)


class SimulationTarget(Base):
    """
    Simulation targets for practice
    FREQ-23: Simulation Environment
    """
    __tablename__ = "simulation_targets"
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Target Details
    name = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=False)  # web, mobile, api, network
    difficulty = Column(String(50), nullable=False)
    
    # Target Configuration
    url = Column(String(500), nullable=True)
    technology_stack = Column(JSON, nullable=True)  # ["React", "Node.js", "PostgreSQL"]
    vulnerabilities = Column(JSON, nullable=True)  # Pre-configured vulnerabilities
    
    # Isolation Settings
    requires_isolation = Column(Boolean, default=True)
    isolation_type = Column(String(50), default="container")  # container, vm, sandbox
    
    # Status
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    simulations = relationship("Simulation", back_populates="target")


class SimulationProgress(Base):
    """
    Simulation progress tracking
    FREQ-24: Simulation Workflow Mirroring
    """
    __tablename__ = "simulation_progress"
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign Key
    simulation_id = Column(UUID(as_uuid=True), ForeignKey("simulations.id"), nullable=False, unique=True)
    
    # Progress Details
    status = Column(String(50), nullable=False)  # reconnaissance, scanning, exploitation, post_exploitation
    current_step = Column(Integer, nullable=False, default=0)
    total_steps = Column(Integer, nullable=False, default=10)
    
    # Performance
    time_spent = Column(Integer, nullable=False, default=0)  # seconds
    hints_used = Column(Integer, nullable=False, default=0)
    
    # Metadata
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    simulation = relationship("Simulation", back_populates="progress")


class SimulationResult(Base):
    """
    Simulation results and scoring
    FREQ-26: Simulation Reporting
    """
    __tablename__ = "simulation_results"
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign Key
    simulation_id = Column(UUID(as_uuid=True), ForeignKey("simulations.id"), nullable=False, unique=True)
    
    # Performance Metrics
    score = Column(Integer, nullable=False)
    accuracy = Column(Integer, nullable=False)  # percentage
    severity_accuracy = Column(Integer, nullable=False)  # percentage
    time_taken = Column(Integer, nullable=False)  # seconds
    hints_used = Column(Integer, nullable=False, default=0)
    
    # Findings
    findings = Column(JSON, nullable=False)  # List of vulnerability findings
    total_findings = Column(Integer, nullable=False, default=0)
    valid_findings = Column(Integer, nullable=False, default=0)
    
    # Completion
    completed_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    simulation = relationship("Simulation", back_populates="result")


class IsolationSession(Base):
    """
    Isolated simulation environment sessions
    FREQ-27: Simulation Data Isolation
    """
    __tablename__ = "isolation_sessions"
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Session Details
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    simulation_id = Column(UUID(as_uuid=True), ForeignKey("simulations.id"), nullable=True)
    target_id = Column(UUID(as_uuid=True), ForeignKey("simulation_targets.id"), nullable=False)
    
    # Isolation Configuration
    isolation_type = Column(String(50), nullable=False, default="container")
    container_id = Column(String(100), nullable=True)  # Docker container ID
    network_id = Column(String(100), nullable=True)  # Network isolation ID
    
    # Session Management
    status = Column(String(50), nullable=False, default="active")  # active, expired, terminated
    started_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    terminated_at = Column(DateTime, nullable=True)
    
    # Resource Limits
    cpu_limit = Column(Integer, nullable=False, default=1)  # CPU cores
    memory_limit = Column(Integer, nullable=False, default=1024)  # MB
    disk_limit = Column(Integer, nullable=False, default=10240)  # MB
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)


class SimulationChallenge(Base):
    """
    Predefined simulation challenges
    FREQ-25: Simulation Difficulty Levels
    """
    __tablename__ = "simulation_challenges"
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Challenge Details
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(100), nullable=False)
    difficulty = Column(String(50), nullable=False)
    
    # Challenge Configuration
    target_id = Column(UUID(as_uuid=True), ForeignKey("simulation_targets.id"), nullable=False)
    objectives = Column(JSON, nullable=False)  # List of objectives
    hints = Column(JSON, nullable=True)  # Available hints
    solution = Column(Text, nullable=True)  # Reference solution
    
    # Scoring
    max_score = Column(Integer, nullable=False, default=100)
    time_limit = Column(Integer, nullable=False)  # seconds
    max_hints = Column(Integer, nullable=False, default=3)
    
    # Status
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    target = relationship("SimulationTarget")
