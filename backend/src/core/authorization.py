"""
Authorization and Resource Ownership Validation
Prevents IDOR (Insecure Direct Object References) attacks
"""
from typing import Optional, Callable
from uuid import UUID
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from src.core.database import get_db
from src.core.config import settings
from src.domain.models.user import User
from src.domain.models.program import BountyProgram
from src.domain.models.researcher import Researcher
from src.domain.models.organization import Organization

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token.
    Uses verify_access_token() so signing and verification use the same key.
    """
    from src.core.security import verify_access_token

    token = credentials.credentials
    payload = verify_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # JWT contains 'user_id' (UUID) and 'sub' (email)
    user_id: str = payload.get("user_id") or payload.get("sub")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Look up user — prefer UUID, fall back to email
    user = None
    try:
        from uuid import UUID as _UUID
        user_uuid = _UUID(str(user_id))
        user = db.query(User).filter(User.id == user_uuid).first()
    except (ValueError, AttributeError):
        user = db.query(User).filter(User.email == user_id).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    return user


def require_role(*allowed_roles: str) -> Callable:
    """
    Dependency to require specific user roles.
    Passing 'admin' automatically accepts 'super_admin' as well.
    """
    # Single admin role for this platform
    expanded = set(allowed_roles)

    def role_checker(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db)
    ) -> User:
        user = get_current_user(credentials, db)

        if user.role not in expanded:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join(allowed_roles)}"
            )

        return user

    return role_checker


class ResourceAuthorization:
    """
    Resource-level authorization checks
    Prevents users from accessing/modifying resources they don't own
    """
    
    @staticmethod
    def verify_program_ownership(
        program: BountyProgram,
        user: User,
        action: str = "modify"
    ) -> bool:
        """
        Verify user owns the program
        
        Args:
            program: The program to check
            user: The current user
            action: The action being performed (view, modify, delete)
        
        Raises:
            HTTPException: If user doesn't have permission
        """
        # Only organizations can own programs
        if user.role != "organization":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Only organizations can {action} programs"
            )
        
        # Check if user's organization owns the program
        if not user.organization or program.organization_id != user.organization.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You don't have permission to {action} this program"
            )
        
        return True
    
    @staticmethod
    def verify_program_access(
        program: BountyProgram,
        user: User,
        db: Session
    ) -> bool:
        """
        Verify user can access the program (view)
        
        - Public programs: anyone can view
        - Private programs: only owner and invited researchers
        """
        from src.services.program_service import ProgramService

        if ProgramService(db).can_user_access_program(program, user):
            return True

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this program"
        )
    
    @staticmethod
    def verify_researcher_profile_ownership(
        researcher_id: UUID,
        user: User
    ) -> bool:
        """Verify user owns the researcher profile"""
        if user.role != "researcher":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only researchers can modify researcher profiles"
            )
        
        if not user.researcher or user.researcher.id != researcher_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only modify your own profile"
            )
        
        return True
    
    @staticmethod
    def verify_organization_profile_ownership(
        organization_id: UUID,
        user: User
    ) -> bool:
        """Verify user owns the organization profile"""
        if user.role != "organization":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only organizations can modify organization profiles"
            )
        
        if not user.organization or user.organization.id != organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only modify your own organization"
            )
        
        return True
    
    @staticmethod
    def verify_invitation_ownership(
        invitation_researcher_id: UUID,
        user: User
    ) -> bool:
        """Verify user owns the invitation (for responding)"""
        if user.role != "researcher":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only researchers can respond to invitations"
            )
        
        if not user.researcher or user.researcher.id != invitation_researcher_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only respond to your own invitations"
            )
        
        return True


class ActionAuthorization:
    """
    Action-level authorization
    Determines what actions users can perform
    """
    
    @staticmethod
    def can_create_program(user: User) -> bool:
        """Check if user can create programs"""
        if user.role != "organization":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only organizations can create programs"
            )
        return True
    
    @staticmethod
    def can_invite_researchers(user: User) -> bool:
        """Check if user can invite researchers"""
        if user.role != "organization":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only organizations can invite researchers"
            )
        return True
    
    @staticmethod
    def can_submit_reports(user: User) -> bool:
        """Check if user can submit vulnerability reports"""
        if user.role != "researcher":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only researchers can submit reports"
            )
        return True
