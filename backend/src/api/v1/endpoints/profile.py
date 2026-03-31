"""
Profile Endpoints - Alias for user profile operations
Provides /profile endpoint as an alias to /users/me for convenience
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.api.v1.middlewares.auth import get_current_user
from src.services.user_service import UserService
from src.domain.models.user import User

router = APIRouter(prefix="/profile", tags=["Profile"])


@router.get("", summary="Get Current User Profile")
def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get current user's profile"""
    service = UserService(db)
    return service.get_profile(str(current_user.id))


@router.put("", summary="Update Current User Profile")
def update_profile(
    data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update current user's profile"""
    service = UserService(db)
    return service.update_profile(str(current_user.id), data, str(current_user.id))
