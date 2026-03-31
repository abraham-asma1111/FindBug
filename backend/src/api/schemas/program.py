"""
Program API Schemas - Fixed for proper validation
"""

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional, Any
from datetime import datetime
from uuid import UUID
import re

class ProgramCreate(BaseModel):
    """Schema for creating bug bounty program"""
    name: str = Field(..., min_length=1, max_length=150)
    description: str = Field(..., min_length=10)
    program_type: str = Field(..., regex="^(public|private|vdp)$")
    scope: Dict[str, Any] = Field(..., description="Program scope configuration")
    reward_tiers: Dict[str, float] = Field(..., description="Reward tiers by severity")
    rules: Optional[str] = Field(None, max_length=5000)
    
    @validator('program_type')
    def validate_program_type(cls, v):
        allowed = ['public', 'private', 'vdp']
        if v not in allowed:
            raise ValueError(f'Program type must be one of: {", ".join(allowed)}')
        return v
    
    @validator('reward_tiers')
    def validate_reward_tiers(cls, v):
        required_keys = ['critical', 'high', 'medium', 'low']
        for key in required_keys:
            if key not in v:
                raise ValueError(f'Reward tier "{key}" is required')
            if not isinstance(v[key], (int, float)) or v[key] <= 0:
                raise ValueError(f'Reward tier "{key}" must be a positive number')
        return v
    
    @validator('scope')
    def validate_scope(cls, v):
        if not isinstance(v, dict):
            raise ValueError('Scope must be a dictionary')
        
        required_fields = ['in_scope', 'out_of_scope']
        for field in required_fields:
            if field not in v:
                raise ValueError(f'Scope must include "{field}"')
        
        return v

class ProgramUpdate(BaseModel):
    """Schema for updating program"""
    name: Optional[str] = Field(None, min_length=1, max_length=150)
    description: Optional[str] = Field(None, min_length=10)
    program_type: Optional[str] = Field(None, regex="^(public|private|vdp)$")
    scope: Optional[Dict[str, Any]] = None
    reward_tiers: Optional[Dict[str, float]] = None
    rules: Optional[str] = Field(None, max_length=5000)
    status: Optional[str] = Field(None, regex="^(active|inactive|archived)$")

class ProgramResponse(BaseModel):
    """Schema for program response"""
    id: UUID
    organization_id: UUID
    name: str
    description: str
    program_type: str
    scope: Dict[str, Any]
    reward_tiers: Dict[str, float]
    rules: Optional[str]
    status: str
    created_at: datetime
    updated_at: Optional[datetime]
    publish_date: Optional[datetime]

    class Config:
        from_attributes = True
