"""Message API endpoints - FREQ-09: Secure in-platform messaging."""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.api.v1.middlewares.auth import get_current_user
from src.domain.models.user import User
from src.services.message_service import MessageService
from src.api.v1.schemas.message import (
    MessageCreate,
    MessageEdit,
    MessageResponse,
    ConversationListResponse,
    MessageListResponse,
    UnreadCountResponse
)


router = APIRouter(prefix="/messages", tags=["messages"])


@router.post("", status_code=status.HTTP_201_CREATED)
@router.get("/send", status_code=status.HTTP_201_CREATED)
def send_message(
    message_data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send a direct message - FREQ-09.
    
    Any authenticated user can send messages to other users.
    """
    service = MessageService(db)
    
    try:
        message = service.send_message(
            sender_id=current_user.id,
            recipient_id=message_data.recipient_id,
            message_text=message_data.message_text
        )
        
        return {
            "message": "Message sent successfully",
            "message_id": str(message.id),
            "conversation_id": str(message.conversation_id)
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send message: {str(e)}"
        )


@router.get("/conversations", response_model=ConversationListResponse)
def get_conversations(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all conversations for current user - FREQ-09.
    
    Returns list of conversations with last message and unread count.
    """
    service = MessageService(db)
    
    try:
        conversations = service.get_conversations(
            user_id=current_user.id,
            limit=limit,
            offset=offset
        )
        
        return {
            "conversations": conversations,
            "total": len(conversations)
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get conversations: {str(e)}"
        )


@router.get("/conversation/{conversation_id}", response_model=MessageListResponse)
def get_conversation_messages(
    conversation_id: UUID,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get messages in a conversation - FREQ-09.
    
    Only participants can view messages.
    """
    service = MessageService(db)
    
    try:
        messages = service.get_messages(
            conversation_id=conversation_id,
            user_id=current_user.id,
            limit=limit,
            offset=offset
        )
        
        return {
            "messages": messages,
            "total": len(messages),
            "conversation_id": conversation_id
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get messages: {str(e)}"
        )


@router.post("/{message_id}/read", status_code=status.HTTP_200_OK)
@router.get("/{message_id}/mark-read", status_code=status.HTTP_200_OK)
def mark_message_as_read(
    message_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark a message as read - FREQ-09.
    
    Only recipient can mark message as read.
    """
    service = MessageService(db)
    
    try:
        message = service.mark_as_read(
            message_id=message_id,
            user_id=current_user.id
        )
        
        return {
            "message": "Message marked as read",
            "message_id": str(message.id),
            "read_at": message.read_at
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark message as read: {str(e)}"
        )


@router.post("/conversation/{conversation_id}/read-all", status_code=status.HTTP_200_OK)
@router.get("/conversation/{conversation_id}/mark-all-read", status_code=status.HTTP_200_OK)
def mark_conversation_as_read(
    conversation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark all messages in conversation as read - FREQ-09.
    
    Only participant can mark messages as read.
    """
    service = MessageService(db)
    
    try:
        count = service.mark_conversation_as_read(
            conversation_id=conversation_id,
            user_id=current_user.id
        )
        
        return {
            "message": f"Marked {count} messages as read",
            "count": count
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark conversation as read: {str(e)}"
        )


@router.get("/unread-count", response_model=UnreadCountResponse)
def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get total unread message count - FREQ-09.
    
    Returns count of unread messages for current user.
    """
    service = MessageService(db)
    
    try:
        count = service.get_unread_count(user_id=current_user.id)
        
        return {
            "unread_count": count
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get unread count: {str(e)}"
        )


@router.put("/{message_id}", status_code=status.HTTP_200_OK)
def edit_message(
    message_id: UUID,
    message_data: MessageEdit,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Edit a message - FREQ-09.
    
    Only sender can edit within 15 minutes of sending.
    """
    service = MessageService(db)
    
    try:
        message = service.edit_message(
            message_id=message_id,
            user_id=current_user.id,
            new_text=message_data.message_text
        )
        
        return {
            "message": "Message edited successfully",
            "message_id": str(message.id),
            "edited": message.edited
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to edit message: {str(e)}"
        )


@router.delete("/{message_id}", status_code=status.HTTP_200_OK)
def delete_message(
    message_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a message - FREQ-09.
    
    Only sender can delete their own messages (soft delete).
    """
    service = MessageService(db)
    
    try:
        message = service.delete_message(
            message_id=message_id,
            user_id=current_user.id
        )
        
        return {
            "message": "Message deleted successfully",
            "message_id": str(message.id)
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete message: {str(e)}"
        )
