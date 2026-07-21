"""
Notification API Schemas
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class EmailPreferencesUpdate(BaseModel):
    """Schema for updating email preferences"""
    report_updates: Optional[bool] = None
    bounty_notifications: Optional[bool] = None
    marketing_emails: Optional[bool] = None
    security_alerts: Optional[bool] = None


class NotificationCreate(BaseModel):
    """Schema for creating notifications"""
    user_id: UUID
    type: str
    title: str
    message: str
    priority: Optional[str] = "medium"
    metadata: Optional[Dict[str, Any]] = None


class NotificationResponse(BaseModel):
    """Schema for notification response"""
    id: UUID
    type: str
    title: str
    message: str
    priority: str
    is_read: bool
    read_at: Optional[datetime] = None
    created_at: datetime
    action_url: Optional[str] = None
    action_text: Optional[str] = None
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[str] = None

    class Config:
        from_attributes = True

class NotificationListResponse(BaseModel):
    """Schema for paginated notification list response"""
    notifications: List[NotificationResponse]
    total: int
    unread_count: int
    limit: int
    offset: int


class NotificationUpdate(BaseModel):
    """Schema for updating notifications"""
    is_read: Optional[bool] = None


class EmailTemplateCreate(BaseModel):
    """Schema for creating email templates"""
    name: str
    subject: str
    body: str
    template_type: str
    variables: Optional[List[str]] = None


class EmailTemplateResponse(BaseModel):
    """Schema for email template response"""
    id: UUID
    name: str
    subject: str
    body: str
    template_type: str
    variables: Optional[List[str]] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class EmailTemplateUpdate(BaseModel):
    """Schema for updating email templates"""
    name: Optional[str] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    is_active: Optional[bool] = None
    variables: Optional[List[str]] = None