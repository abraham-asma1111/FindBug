"""
Email Preferences API Endpoints - Fix for missing 404 endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Optional
from uuid import UUID

from src.core.database import get_db
from src.services.notification_service import NotificationService
from ..schemas.notification import EmailPreferencesUpdate

router = APIRouter(prefix="/email-preferences", tags=["Email Preferences"])

@router.get("/{user_id}")
async def get_email_preferences(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    """Get user's email preferences"""
    try:
        service = NotificationService(db)
        preferences = service.get_email_preferences(str(user_id))
        if not preferences:
            return {
                "report_updates": True,
                "bounty_notifications": True,
                "marketing_emails": False,
                "security_alerts": True
            }
        return preferences
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put("/{user_id}")
async def update_email_preferences(
    user_id: UUID,
    preferences: EmailPreferencesUpdate,
    db: Session = Depends(get_db)
):
    """Update user's email preferences"""
    try:
        service = NotificationService(db)
        success = service.update_email_preferences(str(user_id), preferences.dict())
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return {"message": "Email preferences updated successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/{user_id}/unsubscribe")
async def unsubscribe_from_emails(
    user_id: UUID,
    unsubscribe_data: Dict,
    db: Session = Depends(get_db)
):
    """Unsubscribe from specific email types"""
    try:
        service = NotificationService(db)
        success = service.unsubscribe_from_emails(
            str(user_id),
            unsubscribe_data.get("email_types", [])
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return {"message": "Successfully unsubscribed from selected email types"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
