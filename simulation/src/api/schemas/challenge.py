"""
Challenge API Schemas
"""

from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID


class ChallengeResponse(BaseModel):
    """Challenge response schema"""
    id: UUID
    title: str
    description: str
    category: str
    difficulty: str
    max_score: int
    time_limit: int
    max_hints: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class ChallengeAttempt(BaseModel):
    """Challenge attempt schema"""
    id: UUID
    challenge_id: UUID
    user_id: UUID
    status: str
    started_at: datetime
    submitted_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ChallengeSubmission(BaseModel):
    """Challenge submission schema"""
    solution: str
    time_taken: int
    
    
class HintRequest(BaseModel):
    """Hint request schema"""
    hint_number: int