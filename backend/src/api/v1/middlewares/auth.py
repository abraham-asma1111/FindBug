"""
Authentication Middleware - JWT token validation
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional

from src.core.database import get_db
from src.core.security import TokenSecurity
from src.domain.models.user import User
from src.domain.repositories.user_repository import UserRepository


security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get current authenticated user from JWT token
    
    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials
    
    # Decode and validate token
    payload = TokenSecurity.verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Extract user_id from token
    user_id: str = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Get user from database with eager loading of relationships
    from sqlalchemy.orm import joinedload
    from uuid import UUID
    
    user = db.query(User).options(
        joinedload(User.researcher),
        joinedload(User.organization),
        joinedload(User.staff)
    ).filter(User.id == UUID(user_id)).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    # Check if user is locked
    if user.is_locked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is locked"
        )
    
    return user


async def get_current_verified_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to get current verified user
    
    Raises:
        HTTPException: If user email is not verified
    """
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email verification required"
        )
    
    return current_user


async def get_current_researcher(
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to ensure current user is a researcher
    
    Raises:
        HTTPException: If user is not a researcher
    """
    # Case-insensitive role check
    if current_user.role.upper() != "RESEARCHER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Researcher access required"
        )
    
    return current_user


async def get_current_organization(
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to ensure current user is an organization
    
    Raises:
        HTTPException: If user is not an organization
    """
    from sqlalchemy.orm import joinedload
    
    # Case-insensitive role check (database has uppercase, enum has lowercase)
    if current_user.role.upper() != "ORGANIZATION":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organization access required"
        )
    
    # Eagerly load organization relationship
    user_with_org = db.query(User).options(
        joinedload(User.organization)
    ).filter(User.id == current_user.id).first()
    
    if not user_with_org or not user_with_org.organization:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organization profile not found"
        )
    
    return user_with_org


async def get_current_staff(
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to ensure current user is staff
    
    Raises:
        HTTPException: If user is not staff
    """
    # Case-insensitive role check
    role_upper = current_user.role.upper()
    if role_upper not in ["STAFF", "ADMIN", "SUPER_ADMIN", "TRIAGE_SPECIALIST", "FINANCE_OFFICER"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Staff access required"
        )
    
    return current_user


# Aliases for convenience
require_organization = get_current_organization
require_researcher = get_current_researcher
require_staff = get_current_staff
