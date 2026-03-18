"""Notification API Endpoints - FREQ-12."""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.api.v1.middlewares.auth import get_current_user
from src.domain.models.user import User
from src.services.notification_service import NotificationService


router = APIRouter()


@router.get("/notifications", status_code=status.HTTP_200_OK)
def get_notifications(
    unread_only: bool = Query(False, description="Show only unread notifications"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user notifications - FREQ-12.
    
    Returns in-platform notifications for the current user.
    Supports filtering by read/unread status.
    """
    service = NotificationService(db)
    
    notifications = service.get_user_notifications(
        user_id=current_user.id,
        unread_only=unread_only,
        limit=limit,
        offset=offset
    )
    
    return {
        "notifications": notifications,
        "total": len(notifications),
        "limit": limit,
        "offset": offset
    }


@router.get("/notifications/unread-count", status_code=status.HTTP_200_OK)
def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get count of unread notifications - FREQ-12.
    
    Used for notification badge display.
    """
    service = NotificationService(db)
    
    count = service.get_unread_count(user_id=current_user.id)
    
    return {
        "unread_count": count
    }


@router.post("/notifications/{notification_id}/mark-read", status_code=status.HTTP_200_OK)
@router.get("/notifications/{notification_id}/mark-read", status_code=status.HTTP_200_OK)
def mark_notification_read(
    notification_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark notification as read - FREQ-12.
    
    Updates notification read status and timestamp.
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


@router.post("/notifications/mark-all-read", status_code=status.HTTP_200_OK)
@router.get("/notifications/mark-all-read", status_code=status.HTTP_200_OK)
def mark_all_notifications_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark all notifications as read - FREQ-12.
    
    Bulk operation to mark all user notifications as read.
    """
    service = NotificationService(db)
    
    count = service.mark_all_as_read(user_id=current_user.id)
    
    return {
        "message": f"Marked {count} notifications as read",
        "count": count
    }


@router.delete("/notifications/{notification_id}", status_code=status.HTTP_200_OK)
def delete_notification(
    notification_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a notification - FREQ-12.
    
    Permanently removes notification from user's inbox.
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


@router.get("/notifications/test", status_code=status.HTTP_200_OK)
def test_notification(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Test notification system - Development only.
    
    Creates a test notification for the current user.
    """
    service = NotificationService(db)
    
    from src.domain.models.notification import NotificationType, NotificationPriority
    
    notification = service.create_notification(
        user_id=current_user.id,
        notification_type=NotificationType.ACCOUNT_VERIFIED,
        title="Test Notification",
        message="This is a test notification to verify the notification system is working.",
        priority=NotificationPriority.LOW,
        action_url="/profile",
        action_text="View Profile",
        send_email=False
    )
    
    return {
        "message": "Test notification created",
        "notification": notification
    }
