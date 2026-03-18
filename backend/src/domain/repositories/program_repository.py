"""Program Repository - Database operations for bounty programs."""
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_

from src.domain.models.program import (
    BountyProgram, ProgramScope, RewardTier, ProgramInvitation
)


class ProgramRepository:
    """Repository for bounty program operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    # BountyProgram operations
    def create_program(self, program: BountyProgram) -> BountyProgram:
        """Create a new bounty program."""
        self.db.add(program)
        self.db.commit()
        self.db.refresh(program)
        return program
    
    def get_program_by_id(self, program_id: UUID) -> Optional[BountyProgram]:
        """Get program by ID with all relationships."""
        return self.db.query(BountyProgram).options(
            joinedload(BountyProgram.scopes),
            joinedload(BountyProgram.reward_tiers),
            joinedload(BountyProgram.organization)
        ).filter(
            BountyProgram.id == program_id,
            BountyProgram.deleted_at.is_(None)
        ).first()
    
    def get_programs_by_organization(
        self, 
        organization_id: UUID,
        status: Optional[str] = None
    ) -> List[BountyProgram]:
        """Get all programs for an organization."""
        query = self.db.query(BountyProgram).filter(
            BountyProgram.organization_id == organization_id,
            BountyProgram.deleted_at.is_(None)
        )
        
        if status:
            query = query.filter(BountyProgram.status == status)
        
        return query.order_by(BountyProgram.created_at.desc()).all()
    
    def get_public_programs(
        self,
        status: str = "public",
        limit: int = 50,
        offset: int = 0
    ) -> List[BountyProgram]:
        """Get all public programs."""
        return self.db.query(BountyProgram).filter(
            BountyProgram.visibility == "public",
            BountyProgram.status == status,
            BountyProgram.deleted_at.is_(None)
        ).order_by(
            BountyProgram.created_at.desc()
        ).limit(limit).offset(offset).all()
    
    def update_program(self, program: BountyProgram) -> BountyProgram:
        """Update program."""
        program.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(program)
        return program
    
    def soft_delete_program(self, program_id: UUID) -> bool:
        """Soft delete a program."""
        program = self.get_program_by_id(program_id)
        if program:
            program.deleted_at = datetime.utcnow()
            self.db.commit()
            return True
        return False
    
    # ProgramScope operations
    def add_scope(self, scope: ProgramScope) -> ProgramScope:
        """Add a scope to a program."""
        self.db.add(scope)
        self.db.commit()
        self.db.refresh(scope)
        return scope
    
    def get_scopes_by_program(self, program_id: UUID) -> List[ProgramScope]:
        """Get all scopes for a program."""
        return self.db.query(ProgramScope).filter(
            ProgramScope.program_id == program_id
        ).all()
    
    def update_scope(self, scope: ProgramScope) -> ProgramScope:
        """Update a scope."""
        scope.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(scope)
        return scope
    
    def delete_scope(self, scope_id: UUID) -> bool:
        """Delete a scope."""
        scope = self.db.query(ProgramScope).filter(
            ProgramScope.id == scope_id
        ).first()
        if scope:
            self.db.delete(scope)
            self.db.commit()
            return True
        return False
    
    # RewardTier operations
    def add_reward_tier(self, tier: RewardTier) -> RewardTier:
        """Add a reward tier to a program."""
        self.db.add(tier)
        self.db.commit()
        self.db.refresh(tier)
        return tier
    
    def get_reward_tiers_by_program(self, program_id: UUID) -> List[RewardTier]:
        """Get all reward tiers for a program."""
        return self.db.query(RewardTier).filter(
            RewardTier.program_id == program_id
        ).all()
    
    def update_reward_tier(self, tier: RewardTier) -> RewardTier:
        """Update a reward tier."""
        tier.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(tier)
        return tier
    
    def delete_reward_tier(self, tier_id: UUID) -> bool:
        """Delete a reward tier."""
        tier = self.db.query(RewardTier).filter(
            RewardTier.id == tier_id
        ).first()
        if tier:
            self.db.delete(tier)
            self.db.commit()
            return True
        return False
    
    # ProgramInvitation operations
    def create_invitation(self, invitation: ProgramInvitation) -> ProgramInvitation:
        """Create a program invitation."""
        self.db.add(invitation)
        self.db.commit()
        self.db.refresh(invitation)
        return invitation
    
    def get_invitation_by_id(self, invitation_id: UUID) -> Optional[ProgramInvitation]:
        """Get invitation by ID."""
        return self.db.query(ProgramInvitation).filter(
            ProgramInvitation.id == invitation_id
        ).first()
    
    def get_invitations_by_program(
        self, 
        program_id: UUID,
        status: Optional[str] = None
    ) -> List[ProgramInvitation]:
        """Get all invitations for a program."""
        query = self.db.query(ProgramInvitation).filter(
            ProgramInvitation.program_id == program_id
        )
        
        if status:
            query = query.filter(ProgramInvitation.status == status)
        
        return query.order_by(ProgramInvitation.invited_at.desc()).all()
    
    def get_invitations_by_researcher(
        self,
        researcher_id: UUID,
        status: Optional[str] = None
    ) -> List[ProgramInvitation]:
        """Get all invitations for a researcher."""
        query = self.db.query(ProgramInvitation).filter(
            ProgramInvitation.researcher_id == researcher_id
        )
        
        if status:
            query = query.filter(ProgramInvitation.status == status)
        
        return query.order_by(ProgramInvitation.invited_at.desc()).all()
    
    def update_invitation(self, invitation: ProgramInvitation) -> ProgramInvitation:
        """Update an invitation."""
        self.db.commit()
        self.db.refresh(invitation)
        return invitation
    
    def check_existing_invitation(
        self,
        program_id: UUID,
        researcher_id: UUID
    ) -> Optional[ProgramInvitation]:
        """Check if invitation already exists."""
        return self.db.query(ProgramInvitation).filter(
            ProgramInvitation.program_id == program_id,
            ProgramInvitation.researcher_id == researcher_id,
            ProgramInvitation.status.in_(["pending", "accepted"])
        ).first()
