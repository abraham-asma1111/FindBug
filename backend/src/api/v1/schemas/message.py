"""Message API schemas - FREQ-09."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator


class MessageCreate(BaseModel):
    """Schema for creating a message."""
    
    recipient_id: UUID = Field(..., description="Recipient user ID")
    message_text: str = Field(..., min_length=1, max_length=10000, description="Message content")
    
    @validator('message_text')
    def validate_message_text(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError("Message text cannot be empty")
        return v.strip()


class MessageEdit(BaseModel):
    """Schema for editing a message."""
    
    message_text: str = Field(..., min_length=1, max_length=10000, description="New message content")
    
    @validator('message_text')
    def validate_message_text(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError("Message text cannot be empty")
        return v.strip()


class MessageResponse(BaseModel):
    """Schema for message response."""
    
    id: UUID
    conversation_id: UUID
    sender_id: UUID
    recipient_id: UUID
    message_text: str
    is_read: bool
    read_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    edited: bool
    
    class Config:
        from_attributes = True


class ConversationSummary(BaseModel):
    """Schema for conversation summary."""
    
    conversation_id: str
    other_user: Optional[dict]
    last_message: Optional[dict]
    unread_count: int
    last_message_at: Optional[datetime]
    created_at: datetime


class ConversationListResponse(BaseModel):
    """Schema for conversation list response."""
    
    conversations: list[ConversationSummary]
    total: int


class MessageListResponse(BaseModel):
    """Schema for message list response."""
    
    messages: list[MessageResponse]
    total: int
    conversation_id: UUID


class UnreadCountResponse(BaseModel):
    """Schema for unread count response."""
    
    unread_count: int
