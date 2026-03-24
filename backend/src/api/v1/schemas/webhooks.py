"""
Webhook Schemas — Pydantic models for webhook management (FREQ-42)
"""
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any


class WebhookCreateRequest(BaseModel):
    """Request schema for creating webhook"""
    url: str = Field(..., min_length=1, max_length=500, description="Webhook URL (http:// or https://)")
    events: List[str] = Field(..., min_items=1, description="List of events to subscribe to")
    secret: Optional[str] = Field(None, max_length=100, description="HMAC signing secret (auto-generated if not provided)")


class WebhookUpdateRequest(BaseModel):
    """Request schema for updating webhook"""
    url: Optional[str] = Field(None, min_length=1, max_length=500, description="New webhook URL")
    events: Optional[List[str]] = Field(None, min_items=1, description="New event list")
    is_active: Optional[bool] = Field(None, description="Active status")


class WebhookResponse(BaseModel):
    """Response schema for webhook"""
    webhook_id: str
    organization_id: str
    url: str
    secret: str
    events: List[str]
    is_active: bool
    created_at: str
    updated_at: Optional[str] = None
    message: Optional[str] = None


class WebhookListItem(BaseModel):
    """Single webhook item in list"""
    webhook_id: str
    url: str
    events: List[str]
    is_active: bool
    created_at: str
    updated_at: Optional[str] = None


class WebhookListResponse(BaseModel):
    """Response schema for webhook list"""
    webhooks: List[WebhookListItem]
    total: int
    skip: int
    limit: int


class WebhookLogItem(BaseModel):
    """Single webhook log item"""
    log_id: str
    event: str
    response_status: Optional[int] = None
    error_message: Optional[str] = None
    retry_count: int
    created_at: str


class WebhookLogsResponse(BaseModel):
    """Response schema for webhook logs"""
    logs: List[WebhookLogItem]
    total: int
    skip: int
    limit: int


class WebhookTestResponse(BaseModel):
    """Response schema for webhook test"""
    webhook_id: str
    success: bool
    status_code: Optional[int] = None
    error: Optional[str] = None
    message: str


class WebhookDeleteResponse(BaseModel):
    """Response schema for webhook deletion"""
    webhook_id: str
    message: str


class WebhookTriggerResponse(BaseModel):
    """Response schema for webhook trigger"""
    event: str
    webhooks_triggered: int
    successful: int
    failed: int
    results: List[Dict[str, Any]]


class WebhookEventsResponse(BaseModel):
    """Response schema for supported events"""
    events: List[str]
    total: int
