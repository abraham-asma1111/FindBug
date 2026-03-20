"""
Integration API Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID


class IntegrationCreate(BaseModel):
    """Schema for creating integration"""
    type: str = Field(..., description="Integration type (jira, github, gitlab, azure_devops)")
    config: Dict[str, Any] = Field(..., description="Integration configuration")


class IntegrationUpdate(BaseModel):
    """Schema for updating integration"""
    config: Optional[Dict[str, Any]] = None
    status: Optional[str] = None


class IntegrationResponse(BaseModel):
    """Schema for integration response"""
    id: UUID
    organization_id: UUID
    type: str
    status: str
    config: Dict[str, Any]
    last_sync_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class SyncRequest(BaseModel):
    """Schema for sync request"""
    report_id: UUID
    action: str = Field(..., description="Sync action (create, update, delete)")
    payload: Dict[str, Any]


class SyncResponse(BaseModel):
    """Schema for sync response"""
    task_id: str
    status: str
    message: str


class WebhookEventCreate(BaseModel):
    """Schema for webhook event"""
    event_type: str
    payload: Dict[str, Any]
    signature: Optional[str] = None


class WebhookEventResponse(BaseModel):
    """Schema for webhook event response"""
    id: UUID
    integration_id: UUID
    event_type: str
    is_verified: bool
    processed: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class ConflictResolutionRequest(BaseModel):
    """Schema for conflict resolution"""
    report_id: UUID
    strategy: str = Field(
        default="timestamp",
        description="Resolution strategy (timestamp, local, remote)"
    )


class ConflictResolutionResponse(BaseModel):
    """Schema for conflict resolution response"""
    strategy: str
    winner: str
    message: str


class FieldMappingCreate(BaseModel):
    """Schema for creating field mapping"""
    source_field: str
    target_field: str
    transformation: str = "direct"
    is_required: bool = False
    default_value: Optional[str] = None


class FieldMappingResponse(BaseModel):
    """Schema for field mapping response"""
    id: UUID
    integration_id: UUID
    source_field: str
    target_field: str
    transformation: str
    is_required: bool
    default_value: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class SyncLogResponse(BaseModel):
    """Schema for sync log response"""
    id: UUID
    integration_id: UUID
    report_id: Optional[UUID]
    action: str
    status: str
    error_message: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class TaskStatusResponse(BaseModel):
    """Schema for task status response"""
    task_id: str
    status: str
    result: Optional[Dict[str, Any]]
    error: Optional[str]
