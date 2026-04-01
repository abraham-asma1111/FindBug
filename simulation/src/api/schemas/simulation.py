"""
Simulation API Schemas
"""

from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID


class SimulationCreate(BaseModel):
    """Simulation creation request"""
    user_id: UUID
    target_id: UUID
    level: str


class SimulationUpdate(BaseModel):
    """Simulation progress update"""
    status: str
    current_step: int
    time_spent: int


class SimulationResponse(BaseModel):
    """Simulation response schema"""
    id: UUID
    user_id: UUID
    target_id: UUID
    level: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    expires_at: datetime
    hints_used: int
    time_spent: int
    
    class Config:
        from_attributes = True


class SimulationProgress(BaseModel):
    """Simulation progress schema"""
    id: UUID
    simulation_id: UUID
    status: str
    current_step: int
    total_steps: int
    time_spent: int
    hints_used: int
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SimulationResult(BaseModel):
    """Simulation result schema"""
    id: UUID
    simulation_id: UUID
    score: int
    accuracy: int
    severity_accuracy: int
    time_taken: int
    hints_used: int
    findings: List[Dict[str, Any]]
    total_findings: int
    valid_findings: int
    completed_at: datetime
    
    class Config:
        from_attributes = True


class SimulationRequest(BaseModel):
    """Simulation start request"""
    target_id: UUID
    level: str


class SimulationProgressUpdate(BaseModel):
    """Simulation progress update"""
    status: str
    current_step: int
    time_spent: int


class SimulationResultSubmission(BaseModel):
    """Simulation result submission"""
    findings: List[Dict[str, Any]]
    time_taken: int
    completed: bool