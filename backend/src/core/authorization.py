"""
Authorization and Resource Ownership Validation
Prevents IDOR (Insecure Direct Object References) attacks
"""
from typing import Optional
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.domain.models.user import User
from src.domain.models.program import BountyProgram
from src.domain.models.researcher import Researcher
from src.domain.models.organization import Organization


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
        # Public programs are accessible to all
        if program.visibility == "public":
            return True
        
        # Organization owner can always access
        if user.role == "organization" and user.organization:
            if program.organization_id == user.organization.id:
                return True
        
        # Check if researcher is invited
        if user.role == "researcher" and user.researcher:
            from src.domain.repositories.program_repository import ProgramRepository
            repo = ProgramRepository(db)
            invitation = repo.check_existing_invitation(
                program.id,
                user.researcher.id
            )
            if invitation and invitation.status == "accepted":
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
