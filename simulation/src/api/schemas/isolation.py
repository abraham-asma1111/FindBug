"""
Isolation API Schemas
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class IsolationSessionResponse(BaseModel):
    """Isolation session response"""
    id: UUID
    user_id: UUID
    target_id: UUID
    isolation_type: str
    container_id: Optional[str] = None
    status: str
    started_at: datetime
    expires_at: datetime
    
    class Config:
        from_attributes = True


class IsolationSessionRequest(BaseModel):
    """Isolation session request"""
    target_id: UUID
    isolation_type: str = "container"


class IsolationExtendRequest(BaseModel):
    """Isolation session extension request"""
    extend_minutes: int = 30