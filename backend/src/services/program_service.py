"""Program Service - Business logic for bounty programs."""
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime, timedelta
from decimal import Decimal

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from src.domain.models.program import (
    BountyProgram, ProgramScope, RewardTier, ProgramInvitation
)
from src.domain.repositories.program_repository import ProgramRepository
from src.domain.repositories.organization_repository import OrganizationRepository
from src.domain.repositories.researcher_repository import ResearcherRepository


class ProgramService:
    """Service for managing bounty programs."""
    
    def __init__(self, db: Session):
        self.db = db
        self.program_repo = ProgramRepository(db)
        self.org_repo = OrganizationRepository(db)
        self.researcher_repo = ResearcherRepository(db)
    
    def create_program(
        self,
        organization_id: UUID,
        name: str,
        description: Optional[str],
        program_type: str,
        visibility: str = "private",
        budget: Optional[Decimal] = None,
        policy: Optional[str] = None,
        rules_of_engagement: Optional[str] = None,
        safe_harbor: Optional[str] = None,
        response_sla_hours: int = 72
    ) -> BountyProgram:
        """Create a new bounty program."""
        
        # Verify organization exists
        org = self.org_repo.get_organization_by_id(organization_id)
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )
        
        # Validate program type
        if program_type not in ["bounty", "vdp"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Program type must be 'bounty' or 'vdp'"
            )
        
        # Validate visibility
        if visibility not in ["private", "public"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Visibility must be 'private' or 'public'"
            )
        
        # Create program
        program = BountyProgram(
            id=uuid4(),
            organization_id=organization_id,
            name=name,
            description=description,
            type=program_type,
            status="draft",
            visibility=visibility,
            budget=budget,
            policy=policy,
            rules_of_engagement=rules_of_engagement,
            safe_harbor=safe_harbor,
            response_sla_hours=response_sla_hours
        )
        
        return self.program_repo.create_program(program)
    
    def get_program(self, program_id: UUID) -> BountyProgram:
        """Get program by ID."""
        program = self.program_repo.get_program_by_id(program_id)
        if not program:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Program not found"
            )
        return program
    
    def get_organization_programs(
        self,
        organization_id: UUID,
        status: Optional[str] = None,
        search: Optional[str] = None,
        program_type: Optional[str] = None
    ) -> List[BountyProgram]:
        """Get all programs for an organization with optional filters."""
        from sqlalchemy import or_
        
        query = self.db.query(BountyProgram).filter(
            BountyProgram.organization_id == organization_id,
            BountyProgram.deleted_at.is_(None)
        )
        
        if status:
            query = query.filter(BountyProgram.status == status)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    BountyProgram.name.ilike(search_term),
                    BountyProgram.description.ilike(search_term)
                )
            )
        
        if program_type:
            query = query.filter(BountyProgram.type == program_type)
        
        return query.all()
    
    def get_public_programs(
        self,
        limit: int = 50,
        offset: int = 0
    ) -> List[BountyProgram]:
        """Get all public programs."""
        return self.program_repo.get_public_programs(
            status="public",
            limit=limit,
            offset=offset
        )
    
    def search_public_programs(
        self,
        limit: int = 50,
        offset: int = 0,
        search: Optional[str] = None,
        program_type: Optional[str] = None,
        min_reward: Optional[float] = None,
        max_reward: Optional[float] = None
    ) -> List[BountyProgram]:
        """Search and filter public programs."""
        from sqlalchemy import and_, or_
        from src.domain.models.program import RewardTier
        
        query = self.db.query(BountyProgram).filter(
            BountyProgram.status == "public",
            BountyProgram.deleted_at.is_(None)
        )
        
        # Search by name or description
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    BountyProgram.name.ilike(search_term),
                    BountyProgram.description.ilike(search_term)
                )
            )
        
        # Filter by program type
        if program_type:
            query = query.filter(BountyProgram.type == program_type)
        
        # Filter by reward range
        if min_reward is not None or max_reward is not None:
            query = query.join(RewardTier)
            if min_reward is not None:
                query = query.filter(RewardTier.max_amount >= min_reward)
            if max_reward is not None:
                query = query.filter(RewardTier.min_amount <= max_reward)
        
        return query.offset(offset).limit(limit).all()
    
    def join_program(
        self,
        program_id: UUID,
        researcher_id: UUID
    ):
        """Join a public program."""
        from src.domain.models.program import ProgramParticipation
        from datetime import datetime
        
        # Check if program exists and is public
        program = self.program_repo.get_by_id(program_id)
        if not program:
            raise ValueError("Program not found")
        
        if program.status != "public":
            raise ValueError("Can only join public programs. Private programs require invitation.")
        
        if program.deleted_at:
            raise ValueError("Cannot join archived program")
        
        # Check if already joined
        existing = self.db.query(ProgramParticipation).filter(
            ProgramParticipation.program_id == program_id,
            ProgramParticipation.researcher_id == researcher_id,
            ProgramParticipation.status == "active"
        ).first()
        
        if existing:
            raise ValueError("Already joined this program")
        
        # Create participation
        participation = ProgramParticipation(
            program_id=program_id,
            researcher_id=researcher_id,
            joined_at=datetime.utcnow(),
            status="active"
        )
        
        self.db.add(participation)
        self.db.commit()
        self.db.refresh(participation)
        
        return participation
    
    def get_researcher_participations(
        self,
        researcher_id: UUID
    ) -> List[dict]:
        """Get all programs a researcher has joined."""
        from src.domain.models.program import ProgramParticipation
        
        participations = self.db.query(ProgramParticipation).filter(
            ProgramParticipation.researcher_id == researcher_id,
            ProgramParticipation.status == "active"
        ).all()
        
        result = []
        for participation in participations:
            program = self.program_repo.get_by_id(participation.program_id)
            if program:
                result.append({
                    "program": program,
                    "joined_at": participation.joined_at
                })
        
        return result
    
    def update_program(
        self,
        program_id: UUID,
        organization_id: UUID,
        **updates
    ) -> BountyProgram:
        """Update a program."""
        program = self.get_program(program_id)
        
        # Verify ownership
        if program.organization_id != organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this program"
            )
        
        # Update fields
        for key, value in updates.items():
            if hasattr(program, key) and value is not None:
                setattr(program, key, value)
        
        return self.program_repo.update_program(program)
    
    def publish_program(
        self,
        program_id: UUID,
        organization_id: UUID
    ) -> BountyProgram:
        """Publish a program (change from draft/private to public)."""
        program = self.get_program(program_id)
        
        # Verify ownership
        if program.organization_id != organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to publish this program"
            )
        
        # Validate program has required data
        if not program.scopes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Program must have at least one scope before publishing"
            )
        
        if program.type == "bounty" and not program.reward_tiers:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bounty program must have reward tiers before publishing"
            )
        
        # Update status and visibility
        program.status = "public"
        program.visibility = "public"
        program.start_date = datetime.utcnow()
        
        return self.program_repo.update_program(program)
    
    def add_scope(
        self,
        program_id: UUID,
        organization_id: UUID,
        asset_type: str,
        asset_identifier: str,
        is_in_scope: bool = True,
        description: Optional[str] = None,
        max_severity: Optional[str] = None
    ) -> ProgramScope:
        """Add a scope to a program."""
        program = self.get_program(program_id)
        
        # Verify ownership
        if program.organization_id != organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to modify this program"
            )
        
        # Validate asset type
        valid_types = ["domain", "api", "mobile_app", "web_app", "other"]
        if asset_type not in valid_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Asset type must be one of: {', '.join(valid_types)}"
            )
        
        # Validate severity if provided
        if max_severity:
            valid_severities = ["critical", "high", "medium", "low"]
            if max_severity not in valid_severities:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Severity must be one of: {', '.join(valid_severities)}"
                )
        
        scope = ProgramScope(
            id=uuid4(),
            program_id=program_id,
            asset_type=asset_type,
            asset_identifier=asset_identifier,
            is_in_scope=is_in_scope,
            description=description,
            max_severity=max_severity
        )
        
        return self.program_repo.add_scope(scope)
    
    def set_reward_tiers(
        self,
        program_id: UUID,
        organization_id: UUID,
        tiers: List[Dict[str, Any]]
    ) -> List[RewardTier]:
        """Set reward tiers for a program."""
        program = self.get_program(program_id)
        
        # Verify ownership
        if program.organization_id != organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to modify this program"
            )
        
        # Validate program type
        if program.type != "bounty":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only bounty programs can have reward tiers"
            )
        
        # Delete existing tiers
        existing_tiers = self.program_repo.get_reward_tiers_by_program(program_id)
        for tier in existing_tiers:
            self.program_repo.delete_reward_tier(tier.id)
        
        # Create new tiers
        valid_severities = ["critical", "high", "medium", "low"]
        created_tiers = []
        
        for tier_data in tiers:
            severity = tier_data.get("severity")
            min_amount = tier_data.get("min_amount")
            max_amount = tier_data.get("max_amount")
            
            # Validate
            if severity not in valid_severities:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Severity must be one of: {', '.join(valid_severities)}"
                )
            
            if min_amount >= max_amount:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Min amount must be less than max amount"
                )
            
            tier = RewardTier(
                id=uuid4(),
                program_id=program_id,
                severity=severity,
                min_amount=Decimal(str(min_amount)),
                max_amount=Decimal(str(max_amount))
            )
            
            created_tiers.append(self.program_repo.add_reward_tier(tier))
        
        return created_tiers
    
    def invite_researcher(
        self,
        program_id: UUID,
        organization_id: UUID,
        researcher_id: UUID,
        invited_by_user_id: UUID,
        message: Optional[str] = None,
        expires_in_days: int = 30
    ) -> ProgramInvitation:
        """Invite a researcher to a private program."""
        program = self.get_program(program_id)
        
        # Verify ownership
        if program.organization_id != organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to invite to this program"
            )
        
        # Verify program is private
        if program.visibility != "private":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can only invite researchers to private programs"
            )
        
        # Verify researcher exists
        researcher = self.researcher_repo.get_researcher_by_id(researcher_id)
        if not researcher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Researcher not found"
            )
        
        # Check for existing invitation
        existing = self.program_repo.check_existing_invitation(
            program_id, researcher_id
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Researcher already invited or accepted"
            )
        
        # Create invitation
        invitation = ProgramInvitation(
            id=uuid4(),
            program_id=program_id,
            researcher_id=researcher_id,
            invited_by=invited_by_user_id,
            message=message,
            status="pending",
            expires_at=datetime.utcnow() + timedelta(days=expires_in_days)
        )
        
        return self.program_repo.create_invitation(invitation)
    
    def respond_to_invitation(
        self,
        invitation_id: UUID,
        researcher_id: UUID,
        accept: bool
    ) -> ProgramInvitation:
        """Respond to a program invitation."""
        invitation = self.program_repo.get_invitation_by_id(invitation_id)
        
        if not invitation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invitation not found"
            )
        
        # Verify ownership
        if invitation.researcher_id != researcher_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to respond to this invitation"
            )
        
        # Check if already responded
        if invitation.status != "pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invitation already responded to"
            )
        
        # Check if expired
        if invitation.expires_at < datetime.utcnow():
            invitation.status = "expired"
            self.program_repo.update_invitation(invitation)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invitation has expired"
            )
        
        # Update invitation
        invitation.status = "accepted" if accept else "declined"
        invitation.responded_at = datetime.utcnow()
        
        return self.program_repo.update_invitation(invitation)
