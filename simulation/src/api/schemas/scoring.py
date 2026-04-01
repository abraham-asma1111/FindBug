"""
Scoring API Schemas
"""

from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime
from uuid import UUID


class ScoreResponse(BaseModel):
    """Score response schema"""
    user_id: UUID
    total_score: int
    challenges_completed: int
    average_accuracy: float
    total_time: int
    
    class Config:
        from_attributes = True


class SimulationScoreResponse(BaseModel):
    """Simulation score response"""
    simulation_id: UUID
    score: int
    accuracy: int
    severity_accuracy: int
    time_taken: int
    hints_used: int
    total_findings: int
    valid_findings: int
    
    class Config:
        from_attributes = True


class ScoreCalculationRequest(BaseModel):
    """Score calculation request"""
    findings: List[Dict[str, Any]]
    time_taken: int
    hints_used: int


class FeedbackResponse(BaseModel):
    """Score feedback response"""
    score: int
    feedback: str
    improvement_tips: List[str]
    strengths: List[str]