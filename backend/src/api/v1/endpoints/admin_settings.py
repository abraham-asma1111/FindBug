"""
Admin Settings API Endpoints
"""
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.dependencies import get_current_user
from src.domain.models.user import User, UserRole
from src.services.settings_service import SettingsService
from pydantic import BaseModel

router = APIRouter(prefix="/admin/settings", tags=["Admin Settings"])


class SettingItem(BaseModel):
    value: Any
    type: str = "string"
    description: str = None
    is_public: bool = False

class BulkSettingsUpdate(BaseModel):
    settings: Dict[str, SettingItem]


def check_admin_access(current_user: User = Depends(get_current_user)):
    if current_user.role not in [UserRole.ADMIN.value, UserRole.SUPER_ADMIN.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can access system settings"
        )
    return current_user


@router.get("")
def get_admin_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_access)
):
    """Get all platform settings (Admin only)."""
    settings_service = SettingsService(db)
    return settings_service.get_all_settings(include_private=True)


@router.get("/public")
def get_public_settings(db: Session = Depends(get_db)):
    """Get public platform settings (No auth required)."""
    settings_service = SettingsService(db)
    return settings_service.get_all_settings(include_private=False)


@router.put("/bulk")
def update_bulk_settings(
    payload: BulkSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_access)
):
    """Update multiple system settings."""
    settings_service = SettingsService(db)
    
    # Convert pydantic models to dict
    settings_dict = {
        k: v.dict() for k, v in payload.settings.items()
    }
    
    updated = settings_service.bulk_update_settings(
        settings_dict=settings_dict,
        admin_email=current_user.email
    )
    
    return {
        "message": "Settings updated successfully",
        "updated_keys": list(updated.keys()),
        "settings": updated
    }
