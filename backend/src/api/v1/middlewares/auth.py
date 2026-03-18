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
    
    # Get user from database
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_id)
    
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
    from src.domain.models.user import UserRole
    
    if current_user.role != UserRole.RESEARCHER:
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
    from src.domain.models.user import UserRole
    
    if current_user.role != UserRole.ORGANIZATION:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organization access required"
        )
    
    return current_user


async def get_current_staff(
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to ensure current user is staff
    
    Raises:
        HTTPException: If user is not staff
    """
    from src.domain.models.user import UserRole
    
    if current_user.role not in [UserRole.STAFF, UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Staff access required"
        )
    
    return current_user


# Aliases for convenience
require_organization = get_current_organization
require_researcher = get_current_researcher
require_staff = get_current_staff
