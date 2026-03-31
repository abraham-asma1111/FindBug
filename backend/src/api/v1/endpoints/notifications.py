"""Notification API Endpoints - FREQ-12."""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.api.v1.middlewares.auth import get_current_user
from src.domain.models.user import User
from src.services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", status_code=status.HTTP_200_OK)
def get_notifications(
    unread_only: bool = Query(False, description="Show only unread notifications"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get notifications for current user - FREQ-12.
    
    Returns list of notifications with pagination.
    """
    service = NotificationService(db)
    
    notifications = service.get_user_notifications(
        user_id=current_user.id,
        unread_only=unread_only,
        limit=limit,
        offset=offset
    )
    
    unread_count = service.get_unread_count(current_user.id)
    
    return {
        "notifications": [
            {
                "id": str(n.id),
                "type": n.notification_type.value if hasattr(n.notification_type, 'value') else n.notification_type,
                "priority": n.priority.value if hasattr(n.priority, 'value') else n.priority,
                "title": n.title,
                "message": n.message,
                "is_read": n.is_read,
                "read_at": n.read_at,
                "created_at": n.created_at,
                "action_url": n.action_url,
                "action_text": n.action_text,
                "related_entity_type": n.related_entity_type,
                "related_entity_id": str(n.related_entity_id) if n.related_entity_id else None
            }
            for n in notifications
        ],
        "total": len(notifications),
        "unread_count": unread_count,
        "limit": limit,
        "offset": offset
    }


@router.put("/{notification_id}/read", status_code=status.HTTP_200_OK)
def mark_notification_read(
    notification_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark notification as read - FREQ-12.
    """
    service = NotificationService(db)
    
    try:
        notification = service.mark_as_read(
            notification_id=notification_id,
            user_id=current_user.id
        )
        
        return {
            "message": "Notification marked as read",
            "notification_id": str(notification.id),
            "read_at": notification.read_at
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/mark-all-read", status_code=status.HTTP_200_OK)
def mark_all_notifications_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark all notifications as read - FREQ-12.
    """
    service = NotificationService(db)
    
    count = service.mark_all_as_read(user_id=current_user.id)
    
    return {
        "message": f"Marked {count} notifications as read",
        "count": count
    }


@router.delete("/{notification_id}", status_code=status.HTTP_200_OK)
def delete_notification(
    notification_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete notification - FREQ-12.
    """
    service = NotificationService(db)
    
    try:
        service.delete_notification(
            notification_id=notification_id,
            user_id=current_user.id
        )
        
        return {
            "message": "Notification deleted successfully"
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/unread-count", status_code=status.HTTP_200_OK)
def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get count of unread notifications - FREQ-12.
    """
    service = NotificationService(db)
    
    count = service.get_unread_count(user_id=current_user.id)
    
    return {
        "unread_count": count
    }
