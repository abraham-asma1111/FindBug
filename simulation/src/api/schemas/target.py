"""
Target API Schemas
"""

from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID


class TargetResponse(BaseModel):
    """Target response schema"""
    id: UUID
    name: str
    description: Optional[str] = None
    category: str
    difficulty: str
    url: Optional[str] = None
    technology_stack: Optional[List[str]] = None
    requires_isolation: bool
    isolation_type: str
    is_active: bool
    
    class Config:
        from_attributes = True


class TargetRequest(BaseModel):
    """Target creation request"""
    name: str
    description: Optional[str] = None
    category: str
    difficulty: str
    url: Optional[str] = None
    technology_stack: Optional[List[str]] = None
    requires_isolation: bool = True
    isolation_type: str = "container"