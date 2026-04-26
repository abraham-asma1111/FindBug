"""
User Endpoints — Profile retrieval and updates
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.dependencies import get_current_user, require_admin
from src.services.user_service import UserService
from src.domain.models.user import User

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", summary="Get Current User Profile")
def get_my_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve full profile of the authenticated user."""
    service = UserService(db)
    return service.get_profile(str(current_user.id))


@router.get("/search", summary="Search Users")
def search_users(
    q: str = Query(..., min_length=2, description="Search query (email or name)"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Search for users by email or name to start a conversation."""
    service = UserService(db)
    return service.search_users(q, limit, exclude_user_id=str(current_user.id))


@router.put("/me", summary="Update Current User Profile")
def update_my_profile(
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update profile details of the authenticated user."""
    service = UserService(db)
    return service.update_profile(str(current_user.id), data, str(current_user.id))


@router.get("/{user_id}", summary="Get Public Profile")
def get_public_profile(
    user_id: str,
    db: Session = Depends(get_db),
):
    """Get public profile of a user (researcher or organization)."""
    service = UserService(db)
    return service.get_public_profile(user_id)


# ─── Admin Endpoints ────────────────────────────────────────────────────────


@router.get("", summary="List Users (Admin)")
def list_users(
    role: Optional[str] = Query(None, description="Filter by role"),
    user_status: Optional[str] = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    """List all users (Admin only)."""
    service = UserService(db)
    return service.list_users(role=role, status=user_status, skip=skip, limit=limit)


@router.post("/{user_id}/deactivate", summary="Deactivate User (Admin)")
def deactivate_user(
    user_id: str,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    """Deactivate a user account."""
    service = UserService(db)
    return service.deactivate_user(user_id)


@router.post("/{user_id}/reactivate", summary="Reactivate User (Admin)")
def reactivate_user(
    user_id: str,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    """Reactivate a user account."""
    service = UserService(db)
    return service.reactivate_user(user_id)
