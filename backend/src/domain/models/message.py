"""Message and Conversation domain models - FREQ-09."""
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    Column, String, Text, DateTime, Boolean,
    ForeignKey, func, Index, CheckConstraint
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship

from src.core.database import Base


class Conversation(Base):
    """Conversation model - FREQ-09 (direct messaging)."""
    
    __tablename__ = "conversations"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Participants
    participant_1_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    participant_2_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Metadata
    last_message_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Soft delete
    is_deleted = Column(Boolean, nullable=False, server_default="false")
    
    # Relationships
    participant_1 = relationship("User", foreign_keys=[participant_1_id])
    participant_2 = relationship("User", foreign_keys=[participant_2_id])
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        CheckConstraint('participant_1_id != participant_2_id', name='different_participants'),
        Index('ix_conversations_participant_1', 'participant_1_id'),
        Index('ix_conversations_participant_2', 'participant_2_id'),
        Index('ix_conversations_last_message_at', 'last_message_at'),
    )


class Message(Base):
    """Message model - FREQ-09 (direct messaging)."""
    
    __tablename__ = "messages"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    conversation_id = Column(PGUUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    
    # Message content
    sender_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    recipient_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    message_text = Column(Text, nullable=False)
    
    # Read status
    is_read = Column(Boolean, nullable=False, server_default="false")
    read_at = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Edit tracking
    edited = Column(Boolean, nullable=False, server_default="false")
    
    # Soft delete
    is_deleted = Column(Boolean, nullable=False, server_default="false")
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    sender = relationship("User", foreign_keys=[sender_id])
    recipient = relationship("User", foreign_keys=[recipient_id])
    
    # Indexes
    __table_args__ = (
        Index('ix_messages_conversation_id', 'conversation_id'),
        Index('ix_messages_sender_id', 'sender_id'),
        Index('ix_messages_recipient_id', 'recipient_id'),
        Index('ix_messages_created_at', 'created_at'),
        Index('ix_messages_is_read', 'is_read'),
    )
