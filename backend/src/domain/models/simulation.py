"""
Simulation Platform Domain Models
Handles bug bounty simulation challenges, instances, and reports
"""
from sqlalchemy import Column, String, Integer, Boolean, Text, TIMESTAMP, ForeignKey, JSON, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from backend.src.core.database import Base


class SimulationChallenge(Base):
    """Simulation challenges - vulnerable apps for learning"""
    __tablename__ = "simulation_challenges"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(100))  # xss, sqli, idor, csrf, etc.
    vulnerability_type = Column(String(100))
    
    # Difficulty and Severity
    difficulty_level = Column(String(20))  # beginner, intermediate, advanced, expert
    severity = Column(String(20))  # low, medium, high, critical
    
    points = Column(Integer, default=0)
    estimated_time_minutes = Column(Integer)
    
    # Docker Configuration
    docker_image = Column(String(255), nullable=False)
    docker_registry = Column(String(255))
    container_memory_limit = Column(String(20), default="256m")
    container_cpu_limit = Column(String(20), default="0.5")
    exposed_port = Column(Integer, default=80)
    environment_variables = Column(JSON)
    
    # Learning Resources
    tutorial_video_url = Column(String(500))
    documentation = Column(Text)  # Markdown content
    external_resources = Column(JSON)  # [{title, url}]
    
    # Hints
    hints = Column(JSON)  # {hint1, hint2, hint3}
    hint_costs = Column(JSON)  # {hint1: 0, hint2: 5, hint3: 10}
    
    # Validation
    expected_vulnerability_type = Column(String(100))
    expected_severity = Column(String(20))
    validation_keywords = Column(JSON)
    validation_rules = Column(JSON)
    
    # Solution
    official_solution = Column(Text)
    solution_video_url = Column(String(500))
    
    # Metadata
    is_active = Column(Boolean, default=True)
    is_published = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(TIMESTAMP)
    
    # Stats
    total_attempts = Column(Integer, default=0)
    total_completions = Column(Integer, default=0)
    average_completion_time_minutes = Column(Integer)
    success_rate = Column(Numeric(5, 2))
    
    # Relationships
    instances = relationship("SimulationInstance", back_populates="challenge")
    reports = relationship("SimulationReport", back_populates="challenge")
    solutions = relationship("SimulationSolution", back_populates="challenge")
    progress_records = relationship("SimulationProgress", back_populates="challenge")


class SimulationInstance(Base):
    """Active Docker container instances for challenges"""
    __tablename__ = "simulation_instances"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    instance_id = Column(String(50), unique=True, nullable=False)
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    challenge_id = Column(UUID(as_uuid=True), ForeignKey("simulation_challenges.id"), nullable=False)
    
    container_id = Column(String(100))
    unique_url = Column(String(500))
    port = Column(Integer)
    
    status = Column(String(20), default="running")  # running, stopped, expired
    
    started_at = Column(TIMESTAMP, default=datetime.utcnow)
    expires_at = Column(TIMESTAMP)
    stopped_at = Column(TIMESTAMP)
    
    # Relationships
    user = relationship("User")
    challenge = relationship("SimulationChallenge", back_populates="instances")


class SimulationProgress(Base):
    """Track user progress through challenges"""
    __tablename__ = "simulation_progress"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    challenge_id = Column(UUID(as_uuid=True), ForeignKey("simulation_challenges.id"), nullable=False)
    
    status = Column(String(20), default="not_started")  # not_started, in_progress, completed
    attempts = Column(Integer, default=0)
    hints_used = Column(Integer, default=0)
    
    completed_at = Column(TIMESTAMP)
    time_spent_seconds = Column(Integer, default=0)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
    challenge = relationship("SimulationChallenge", back_populates="progress_records")


class SimulationReport(Base):
    """Simulation vulnerability reports (practice reports)"""
    __tablename__ = "simulation_reports"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    challenge_id = Column(UUID(as_uuid=True), ForeignKey("simulation_challenges.id"), nullable=False)
    
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    steps_to_reproduce = Column(Text, nullable=False)
    impact_assessment = Column(Text)
    suggested_severity = Column(String(20))
    proof_of_concept = Column(Text)
    
    status = Column(String(20), default="submitted")  # submitted, validated, invalid
    is_correct = Column(Boolean)
    feedback = Column(Text)
    points_awarded = Column(Integer, default=0)
    
    submitted_at = Column(TIMESTAMP, default=datetime.utcnow)
    validated_at = Column(TIMESTAMP)
    
    # Relationships
    user = relationship("User")
    challenge = relationship("SimulationChallenge", back_populates="reports")


class SimulationSolution(Base):
    """Community-submitted solutions (writeups)"""
    __tablename__ = "simulation_solutions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    challenge_id = Column(UUID(as_uuid=True), ForeignKey("simulation_challenges.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    title = Column(String(255), nullable=False)
    content = Column(Text)  # Markdown writeup
    video_url = Column(String(500))
    
    is_approved = Column(Boolean, default=False)
    likes_count = Column(Integer, default=0)
    views_count = Column(Integer, default=0)
    
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    challenge = relationship("SimulationChallenge", back_populates="solutions")
    user = relationship("User")
    comments = relationship("SimulationSolutionComment", back_populates="solution")
    likes = relationship("SimulationSolutionLike", back_populates="solution")


class SimulationSolutionComment(Base):
    """Comments on community solutions"""
    __tablename__ = "simulation_solution_comments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    solution_id = Column(UUID(as_uuid=True), ForeignKey("simulation_solutions.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    content = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    
    # Relationships
    solution = relationship("SimulationSolution", back_populates="comments")
    user = relationship("User")


class SimulationSolutionLike(Base):
    """Likes on community solutions"""
    __tablename__ = "simulation_solution_likes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    solution_id = Column(UUID(as_uuid=True), ForeignKey("simulation_solutions.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    
    # Relationships
    solution = relationship("SimulationSolution", back_populates="likes")
    user = relationship("User")


class SimulationLeaderboard(Base):
    """Leaderboard for simulation mode"""
    __tablename__ = "simulation_leaderboard"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False)
    
    total_points = Column(Integer, default=0)
    challenges_completed = Column(Integer, default=0)
    rank = Column(Integer)
    last_updated = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
