"""Message Service - FREQ-09: Secure in-platform messaging."""
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from sqlalchemy import or_, and_, func
from sqlalchemy.orm import Session

from src.domain.models.message import Message, Conversation
from src.domain.models.user import User
from src.services.security_service import SecurityService


class MessageService:
    """Service for managing direct messages between users."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_or_create_conversation(
        self,
        user_1_id: UUID,
        user_2_id: UUID
    ) -> Conversation:
        """
        Get existing conversation or create new one.
        
        Args:
            user_1_id: First participant ID
            user_2_id: Second participant ID
            
        Returns:
            Conversation object
        """
        # Check if conversation exists (either direction)
        conversation = self.db.query(Conversation).filter(
            or_(
                and_(
                    Conversation.participant_1_id == user_1_id,
                    Conversation.participant_2_id == user_2_id
                ),
                and_(
                    Conversation.participant_1_id == user_2_id,
                    Conversation.participant_2_id == user_1_id
                )
            ),
            Conversation.is_deleted == False
        ).first()
        
        if conversation:
            return conversation
        
        # Create new conversation
        conversation = Conversation(
            participant_1_id=user_1_id,
            participant_2_id=user_2_id
        )
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        
        return conversation
    
    def send_message(
        self,
        sender_id: UUID,
        recipient_id: UUID,
        message_text: str
    ) -> Message:
        """
        Send a direct message.
        
        Args:
            sender_id: Sender user ID
            recipient_id: Recipient user ID
            message_text: Message content
            
        Returns:
            Created message
            
        Raises:
            ValueError: If validation fails
        """
        # Validate message text
        if not message_text or len(message_text.strip()) == 0:
            raise ValueError("Message text cannot be empty")
        
        if len(message_text) > 10000:
            raise ValueError("Message text cannot exceed 10,000 characters")
        
        # Simple sanitization - just strip whitespace
        sanitized_text = message_text.strip()
        
        # Verify users exist
        sender = self.db.query(User).filter(User.id == sender_id).first()
        recipient = self.db.query(User).filter(User.id == recipient_id).first()
        
        if not sender:
            raise ValueError("Sender not found")
        if not recipient:
            raise ValueError("Recipient not found")
        
        if sender_id == recipient_id:
            raise ValueError("Cannot send message to yourself")
        
        # Get or create conversation
        conversation = self.get_or_create_conversation(sender_id, recipient_id)
        
        # Create message
        message = Message(
            conversation_id=conversation.id,
            sender_id=sender_id,
            recipient_id=recipient_id,
            message_text=sanitized_text
        )
        
        self.db.add(message)
        
        # Update conversation last_message_at
        conversation.last_message_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(message)
        
        return message
    
    def get_conversations(
        self,
        user_id: UUID,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get all conversations for a user.
        
        Args:
            user_id: User ID
            limit: Maximum number of conversations
            offset: Pagination offset
            
        Returns:
            List of conversations with metadata
        """
        conversations = self.db.query(Conversation).filter(
            or_(
                Conversation.participant_1_id == user_id,
                Conversation.participant_2_id == user_id
            ),
            Conversation.is_deleted == False
        ).order_by(
            Conversation.last_message_at.desc().nullslast()
        ).limit(limit).offset(offset).all()
        
        result = []
        for conv in conversations:
            # Determine other participant
            other_user_id = (
                conv.participant_2_id 
                if conv.participant_1_id == user_id 
                else conv.participant_1_id
            )
            
            other_user = self.db.query(User).filter(User.id == other_user_id).first()
            
            # Get last message
            last_message = self.db.query(Message).filter(
                Message.conversation_id == conv.id,
                Message.is_deleted == False
            ).order_by(Message.created_at.desc()).first()
            
            # Count unread messages
            unread_count = self.db.query(func.count(Message.id)).filter(
                Message.conversation_id == conv.id,
                Message.recipient_id == user_id,
                Message.is_read == False,
                Message.is_deleted == False
            ).scalar()
            
            result.append({
                "conversation_id": str(conv.id),
                "other_user": {
                    "id": str(other_user.id),
                    "email": other_user.email,
                    "role": other_user.role
                } if other_user else None,
                "last_message": {
                    "text": last_message.message_text[:100],
                    "created_at": last_message.created_at,
                    "sender_id": str(last_message.sender_id)
                } if last_message else None,
                "unread_count": unread_count,
                "last_message_at": conv.last_message_at,
                "created_at": conv.created_at
            })
        
        return result
    
    def get_messages(
        self,
        conversation_id: UUID,
        user_id: UUID,
        limit: int = 100,
        offset: int = 0
    ) -> List[Message]:
        """
        Get messages in a conversation.
        
        Args:
            conversation_id: Conversation ID
            user_id: Requesting user ID (for access control)
            limit: Maximum number of messages
            offset: Pagination offset
            
        Returns:
            List of messages
            
        Raises:
            ValueError: If user is not participant
        """
        # Verify user is participant
        conversation = self.db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()
        
        if not conversation:
            raise ValueError("Conversation not found")
        
        if user_id not in [conversation.participant_1_id, conversation.participant_2_id]:
            raise ValueError("Access denied: not a participant")
        
        # Get messages
        messages = self.db.query(Message).filter(
            Message.conversation_id == conversation_id,
            Message.is_deleted == False
        ).order_by(
            Message.created_at.asc()
        ).limit(limit).offset(offset).all()
        
        return messages
    
    def mark_as_read(
        self,
        message_id: UUID,
        user_id: UUID
    ) -> Message:
        """
        Mark a message as read.
        
        Args:
            message_id: Message ID
            user_id: User ID (must be recipient)
            
        Returns:
            Updated message
            
        Raises:
            ValueError: If validation fails
        """
        message = self.db.query(Message).filter(
            Message.id == message_id
        ).first()
        
        if not message:
            raise ValueError("Message not found")
        
        if message.recipient_id != user_id:
            raise ValueError("Only recipient can mark message as read")
        
        if not message.is_read:
            message.is_read = True
            message.read_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(message)
        
        return message
    
    def mark_conversation_as_read(
        self,
        conversation_id: UUID,
        user_id: UUID
    ) -> int:
        """
        Mark all messages in conversation as read.
        
        Args:
            conversation_id: Conversation ID
            user_id: User ID (recipient)
            
        Returns:
            Number of messages marked as read
        """
        # Verify user is participant
        conversation = self.db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()
        
        if not conversation:
            raise ValueError("Conversation not found")
        
        if user_id not in [conversation.participant_1_id, conversation.participant_2_id]:
            raise ValueError("Access denied: not a participant")
        
        # Mark all unread messages as read
        count = self.db.query(Message).filter(
            Message.conversation_id == conversation_id,
            Message.recipient_id == user_id,
            Message.is_read == False,
            Message.is_deleted == False
        ).update({
            "is_read": True,
            "read_at": datetime.utcnow()
        })
        
        self.db.commit()
        
        return count
    
    def get_unread_count(self, user_id: UUID) -> int:
        """
        Get total unread message count for user.
        
        Args:
            user_id: User ID
            
        Returns:
            Number of unread messages
        """
        count = self.db.query(func.count(Message.id)).filter(
            Message.recipient_id == user_id,
            Message.is_read == False,
            Message.is_deleted == False
        ).scalar()
        
        return count or 0
    
    def edit_message(
        self,
        message_id: UUID,
        user_id: UUID,
        new_text: str
    ) -> Message:
        """
        Edit a message (within 15 minutes).
        
        Args:
            message_id: Message ID
            user_id: User ID (must be sender)
            new_text: New message text
            
        Returns:
            Updated message
            
        Raises:
            ValueError: If validation fails
        """
        message = self.db.query(Message).filter(
            Message.id == message_id
        ).first()
        
        if not message:
            raise ValueError("Message not found")
        
        if message.sender_id != user_id:
            raise ValueError("Only sender can edit message")
        
        # Check 15-minute edit window
        time_diff = (datetime.utcnow() - message.created_at).total_seconds()
        if time_diff > 900:  # 15 minutes
            raise ValueError("Edit window expired (15 minutes)")
        
        # Validate new text
        if not new_text or len(new_text.strip()) == 0:
            raise ValueError("Message text cannot be empty")
        
        if len(new_text) > 10000:
            raise ValueError("Message text cannot exceed 10,000 characters")
        
        # Simple sanitization - just strip whitespace
        sanitized_text = new_text.strip()
        message.message_text = sanitized_text
        message.edited = True
        message.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(message)
        
        return message
    
    def delete_message(
        self,
        message_id: UUID,
        user_id: UUID
    ) -> Message:
        """
        Soft delete a message.
        
        Args:
            message_id: Message ID
            user_id: User ID (must be sender)
            
        Returns:
            Deleted message
            
        Raises:
            ValueError: If validation fails
        """
        message = self.db.query(Message).filter(
            Message.id == message_id
        ).first()
        
        if not message:
            raise ValueError("Message not found")
        
        if message.sender_id != user_id:
            raise ValueError("Only sender can delete message")
        
        message.is_deleted = True
        message.deleted_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(message)
        
        return message
