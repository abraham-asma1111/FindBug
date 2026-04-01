"""
FastAPI dependency injection functions for FindBug Platform
"""
from typing import Optional
from fastapi import Depends, Header
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.security import verify_access_token
from src.core.exceptions import UnauthorizedException, ForbiddenException
from src.domain.repositories.user_repository import UserRepository
from src.utils.constants import UserRole


def _get_user_from_token_claims(
    repo: UserRepository,
    user_id_claim: Optional[str],
    email_claim: Optional[str],
):
    """Resolve the authenticated user from explicit token claims."""
    if user_id_claim:
        return repo.get_by_id(user_id_claim)
    if email_claim:
        return repo.get_by_email(email_claim)
    return None


# ─── Bearer token extraction ─────────────────────────────────────────────────
def get_token_from_header(authorization: Optional[str] = Header(None)) -> str:
    """Extract JWT from the Authorization: Bearer <token> header."""
    if not authorization or not authorization.startswith("Bearer "):
        raise UnauthorizedException("Missing or invalid Authorization header.")
    return authorization.split(" ", 1)[1]


# ─── Current user ─────────────────────────────────────────────────────────────
def get_current_user(
    token: str = Depends(get_token_from_header),
    db: Session = Depends(get_db),
):
    """
    Decode JWT and return the authenticated User ORM object.
    Raises 401 if token is invalid or user does not exist.
    """
    payload = verify_access_token(token)
    if not payload:
        raise UnauthorizedException("Invalid or expired token.")

    user_id_claim = payload.get("user_id")
    email_claim = payload.get("sub")
    if not user_id_claim and not email_claim:
        raise UnauthorizedException("Token missing user identifier.")

    repo = UserRepository(db)
    try:
        user = _get_user_from_token_claims(repo, user_id_claim, email_claim)
    except (ValueError, TypeError, AttributeError) as exc:
        raise UnauthorizedException("Token missing valid user identifier.") from exc
    
    if not user:
        raise UnauthorizedException("User account not found.")
    if not user.is_active:
        raise UnauthorizedException("User account is deactivated.")
    return user


def get_current_user_optional(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    """Return current user or None (for public endpoints that optionally auth)."""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.split(" ", 1)[1]
    payload = verify_access_token(token)
    if not payload:
        return None
    user_id_claim = payload.get("user_id")
    email_claim = payload.get("sub")
    if not user_id_claim and not email_claim:
        return None
    repo = UserRepository(db)
    try:
        return _get_user_from_token_claims(repo, user_id_claim, email_claim)
    except (ValueError, TypeError, AttributeError):
        return None


def get_current_verified_user(
    current_user=Depends(get_current_user),
):
    """
    Return current user only if email is verified.
    Raises 403 if email not verified.
    """
    if not current_user.email_verified:
        raise ForbiddenException("Email verification required.")
    return current_user


def get_current_researcher(
    current_user=Depends(get_current_user),
):
    """
    Return current user only if role is researcher.
    Raises 403 if not a researcher.
    """
    if current_user.role != UserRole.RESEARCHER:
        raise ForbiddenException("Researcher role required.")
    return current_user


def get_current_organization(
    current_user=Depends(get_current_user),
):
    """
    Return current user only if role is organization.
    Raises 403 if not an organization.
    """
    if current_user.role != UserRole.ORGANIZATION:
        raise ForbiddenException("Organization role required.")
    return current_user


# ─── Role guards ──────────────────────────────────────────────────────────────
def require_role(*roles: str):
    """
    Dependency factory that enforces one of the given roles.

    Usage:
        @router.get("/admin", dependencies=[Depends(require_role("admin", "staff"))])
    """
    def _check(current_user=Depends(get_current_user)):
        if current_user.role not in roles:
            raise ForbiddenException(
                f"This action requires one of the following roles: {', '.join(roles)}."
            )
        return current_user
    return _check


def require_researcher(current_user=Depends(get_current_user)):
    """Shortcut: require researcher role."""
    if current_user.role != UserRole.RESEARCHER:
        raise ForbiddenException("Only researchers can perform this action.")
    return current_user


def require_organization(current_user=Depends(get_current_user)):
    """Shortcut: require organization role."""
    if current_user.role != UserRole.ORGANIZATION:
        raise ForbiddenException("Only organizations can perform this action.")
    return current_user


def require_admin(current_user=Depends(get_current_user)):
    """Shortcut: require admin or staff role."""
    if current_user.role not in (UserRole.ADMIN, UserRole.STAFF):
        raise ForbiddenException("Admin access required.")
    return current_user


def require_triage(current_user=Depends(get_current_user)):
    """Shortcut: require triage_specialist, staff, or admin."""
    allowed = {UserRole.TRIAGE_SPECIALIST, UserRole.STAFF, UserRole.ADMIN}
    if current_user.role not in allowed:
        raise ForbiddenException("Triage specialist access required.")
    return current_user


def require_financial(current_user=Depends(get_current_user)):
    """Shortcut: require financial_officer, staff, or admin."""
    allowed = {UserRole.FINANCIAL_OFFICER, UserRole.STAFF, UserRole.ADMIN}
    if current_user.role not in allowed:
        raise ForbiddenException("Financial officer access required.")
    return current_user
