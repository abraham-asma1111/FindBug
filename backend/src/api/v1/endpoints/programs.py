"""Program API Endpoints."""
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.api.v1.middlewares.auth import get_current_user, require_organization
from src.domain.models.user import User
from src.domain.models.program import BountyProgram
from src.services.program_service import ProgramService
from src.api.v1.schemas.program import (
    ProgramCreate, ProgramUpdate, ProgramResponse, ProgramListResponse,
    ScopeCreate, ScopeResponse,
    RewardTierResponse, BulkRewardTiersCreate,
    InvitationCreate, InvitationResponse, InvitationRespond
)

router = APIRouter(prefix="/programs", tags=["programs"])


@router.post("", response_model=ProgramResponse, status_code=status.HTTP_201_CREATED)
def create_program(
    program_data: ProgramCreate,
    current_user: User = Depends(require_organization),
    db: Session = Depends(get_db)
):
    """
    Create a new bounty program.
    
    Only organizations can create programs.
    """
    try:
        service = ProgramService(db)
        
        program = service.create_program(
            organization_id=str(current_user.organization.id),
            name=program_data.name,
            description=program_data.description,
            program_type=program_data.type
        )
        
        return ProgramResponse.from_orm(program)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("", response_model=List[ProgramListResponse])
def list_programs(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    search: Optional[str] = Query(None, description="Search by program name or description"),
    program_type: Optional[str] = Query(None, description="Filter by type: bounty or vdp"),
    program_status: Optional[str] = Query(None, description="Filter by status: draft, public, paused, closed"),
    min_reward: Optional[float] = Query(None, description="Minimum reward amount"),
    max_reward: Optional[float] = Query(None, description="Maximum reward amount"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List and search programs with filters.
    
    - Organizations see their own programs
    - Researchers see public programs
    - Supports search and filtering
    """
    service = ProgramService(db)
    
    if current_user.is_organization():
        programs = service.get_organization_programs(
            current_user.organization.id,
            search=search,
            program_type=program_type,
            status=program_status
        )
    else:
        programs = service.search_public_programs(
            limit=limit,
            offset=offset,
            search=search,
            program_type=program_type,
            min_reward=min_reward,
            max_reward=max_reward
        )
    
    return programs


@router.get("/my-programs", response_model=List[ProgramListResponse])
def get_my_programs(
    program_status: str = Query(None, description="Filter by status"),
    current_user: User = Depends(require_organization),
    db: Session = Depends(get_db)
):
    """
    Get all programs for the current organization.
    
    Only organizations can access this endpoint.
    """
    service = ProgramService(db)
    
    programs = service.get_organization_programs(
        current_user.organization.id,
        status=program_status
    )
    
    return programs


@router.get("/archived", response_model=List[ProgramListResponse])
def get_archived_programs(
    current_user: User = Depends(require_organization),
    db: Session = Depends(get_db)
):
    """
    Get all archived programs for the current organization.
    
    Only organizations can access this endpoint.
    """
    # Get archived programs (those with deleted_at set)
    programs = db.query(BountyProgram).filter(
        BountyProgram.organization_id == current_user.organization.id,
        BountyProgram.deleted_at.isnot(None)
    ).order_by(BountyProgram.deleted_at.desc()).all()
    
    return programs


@router.get("/my-participations", status_code=status.HTTP_200_OK)
def get_my_participations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get programs the researcher has joined.
    
    Only for researchers.
    """
    if not current_user.is_researcher():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only researchers can view participations"
        )
    
    service = ProgramService(db)
    
    participations = service.get_researcher_participations(
        researcher_id=current_user.researcher.id
    )
    
    return participations


@router.get("/{program_id}", response_model=ProgramResponse)
def get_program(
    program_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get program details.
    
    - Public programs: accessible to all
    - Private programs: only accessible to organization owner and invited researchers
    """
    service = ProgramService(db)
    program = service.get_program(program_id)
    
    # Check access
    if program.visibility == "private":
        # Organization owner can access
        if current_user.is_organization() and program.organization_id == current_user.organization.id:
            return program
        
        # Invited researchers can access
        if current_user.is_researcher():
            invitation = service.program_repo.check_existing_invitation(
                program_id, current_user.researcher.id
            )
            if invitation and invitation.status == "accepted":
                return program
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this program"
        )
    
    return program


@router.post("/{program_id}/update", response_model=ProgramResponse)
@router.get("/{program_id}/update", response_model=ProgramResponse)
def update_program(
    program_id: UUID,
    program_data: ProgramUpdate = None,
    current_user: User = Depends(require_organization),
    db: Session = Depends(get_db)
):
    """
    Update a program.
    
    Only the organization that owns the program can update it.
    Supports both GET and POST methods.
    """
    service = ProgramService(db)
    
    # For GET requests without data, just return the current program
    if program_data is None:
        return service.get_program(program_id)
    
    updates = program_data.dict(exclude_unset=True)
    program = service.update_program(
        program_id,
        current_user.organization.id,
        **updates
    )
    
    return program


@router.post("/{program_id}/publish", response_model=ProgramResponse)
@router.get("/{program_id}/publish", response_model=ProgramResponse)
def publish_program(
    program_id: UUID,
    current_user: User = Depends(require_organization),
    db: Session = Depends(get_db)
):
    """
    Publish a program (make it public).
    
    Program must have at least one scope and reward tiers (for bounty programs).
    Organization must have sufficient wallet balance (≥ critical tier reward).
    Supports both GET and POST methods.
    """
    service = ProgramService(db)
    
    # Get program to check reward tiers
    program = service.get_program(program_id)
    
    # Verify ownership
    if program.organization_id != current_user.organization.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to publish this program"
        )
    
    # Check wallet balance for bounty programs
    if program.type == "bounty":
        # Get reward tiers
        tiers = service.program_repo.get_reward_tiers_by_program(program_id)
        
        if not tiers:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot publish bounty program without reward tiers"
            )
        
        # Find critical tier (highest max_amount)
        critical_tier = max(tiers, key=lambda t: t.max_amount)
        critical_amount = critical_tier.max_amount
        
        # Check organization wallet balance
        from src.services.wallet_service import WalletService
        wallet_service = WalletService(db)
        
        try:
            balance_info = wallet_service.get_balance(
                owner_id=current_user.id,
                owner_type="organization"
            )
            
            current_balance = balance_info.get("balance", 0)
            
            if current_balance < critical_amount:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient wallet balance. You need at least {critical_amount} ETB (critical tier max reward) to publish this program. Current balance: {current_balance} ETB. Please recharge your wallet."
                )
        except Exception as e:
            # If wallet doesn't exist or other error, block publish
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unable to verify wallet balance: {str(e)}. Please ensure your wallet is set up and has sufficient funds."
            )
    
    # Proceed with publish
    program = service.publish_program(
        program_id,
        current_user.organization.id
    )
    
    return program


@router.post("/{program_id}/scopes", response_model=ScopeResponse, status_code=status.HTTP_201_CREATED)
@router.get("/{program_id}/scopes/add", response_model=ScopeResponse, status_code=status.HTTP_201_CREATED)
def add_scope(
    program_id: UUID,
    scope_data: ScopeCreate = None,
    current_user: User = Depends(require_organization),
    db: Session = Depends(get_db)
):
    """
    Add a scope to a program.
    
    Only the organization that owns the program can add scopes.
    Supports both GET and POST methods.
    """
    if scope_data is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Scope data required"
        )
    
    service = ProgramService(db)
    
    scope = service.add_scope(
        program_id=program_id,
        organization_id=current_user.organization.id,
        asset_type=scope_data.asset_type,
        asset_identifier=scope_data.asset_identifier,
        is_in_scope=scope_data.is_in_scope,
        description=scope_data.description,
        max_severity=scope_data.max_severity
    )
    
    return scope


@router.get("/{program_id}/scopes", response_model=List[ScopeResponse])
def get_scopes(
    program_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all scopes for a program."""
    service = ProgramService(db)
    
    # Verify access to program
    program = service.get_program(program_id)
    
    if program.visibility == "private":
        if current_user.is_organization() and program.organization_id != current_user.organization.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this program"
            )
    
    scopes = service.program_repo.get_scopes_by_program(program_id)
    return scopes


@router.post("/{program_id}/rewards", response_model=List[RewardTierResponse], status_code=status.HTTP_201_CREATED)
@router.get("/{program_id}/rewards/set", response_model=List[RewardTierResponse], status_code=status.HTTP_201_CREATED)
def set_reward_tiers(
    program_id: UUID,
    tiers_data: BulkRewardTiersCreate = None,
    current_user: User = Depends(require_organization),
    db: Session = Depends(get_db)
):
    """
    Set reward tiers for a program.
    
    This replaces all existing reward tiers.
    Only the organization that owns the program can set reward tiers.
    Supports both GET and POST methods.
    """
    if tiers_data is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reward tiers data required"
        )
    
    service = ProgramService(db)
    
    tiers = service.set_reward_tiers(
        program_id=program_id,
        organization_id=current_user.organization.id,
        tiers=[tier.dict() for tier in tiers_data.tiers]
    )
    
    return tiers


@router.get("/{program_id}/rewards", response_model=List[RewardTierResponse])
def get_reward_tiers(
    program_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all reward tiers for a program."""
    service = ProgramService(db)
    
    # Verify access to program
    program = service.get_program(program_id)
    
    if program.visibility == "private":
        if current_user.is_organization() and program.organization_id != current_user.organization.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this program"
            )
    
    tiers = service.program_repo.get_reward_tiers_by_program(program_id)
    return tiers


@router.post("/{program_id}/invite", response_model=InvitationResponse, status_code=status.HTTP_201_CREATED)
def invite_researcher(
    program_id: UUID,
    invitation_data: InvitationCreate,
    current_user: User = Depends(require_organization),
    db: Session = Depends(get_db)
):
    """
    Invite a researcher to a private program.
    
    Only the organization that owns the program can invite researchers.
    """
    service = ProgramService(db)
    
    invitation = service.invite_researcher(
        program_id=program_id,
        organization_id=current_user.organization.id,
        researcher_id=invitation_data.researcher_id,
        invited_by_user_id=current_user.id,
        message=invitation_data.message,
        expires_in_days=invitation_data.expires_in_days
    )
    
    return invitation


@router.get("/{program_id}/invitations", response_model=List[InvitationResponse])
def get_program_invitations(
    program_id: UUID,
    invitation_status: str = Query(None, description="Filter by status"),
    current_user: User = Depends(require_organization),
    db: Session = Depends(get_db)
):
    """
    Get all invitations for a program.
    
    Only the organization that owns the program can view invitations.
    """
    service = ProgramService(db)
    
    # Verify ownership
    program = service.get_program(program_id)
    if program.organization_id != current_user.organization.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view invitations for this program"
        )
    
    invitations = service.program_repo.get_invitations_by_program(
        program_id, status=invitation_status
    )
    
    return invitations


@router.get("/invitations/my-invitations", response_model=List[InvitationResponse])
def get_my_invitations(
    invitation_status: str = Query(None, description="Filter by status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all invitations for the current researcher.
    
    Only researchers can access this endpoint.
    """
    if not current_user.is_researcher():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only researchers can view invitations"
        )
    
    service = ProgramService(db)
    
    invitations = service.program_repo.get_invitations_by_researcher(
        current_user.researcher.id, status=invitation_status
    )
    
    return invitations


@router.post("/invitations/{invitation_id}/respond", response_model=InvitationResponse)
def respond_to_invitation(
    invitation_id: UUID,
    response_data: InvitationRespond,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Respond to a program invitation.
    
    Only the invited researcher can respond.
    """
    if not current_user.is_researcher():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only researchers can respond to invitations"
        )
    
    service = ProgramService(db)
    
    invitation = service.respond_to_invitation(
        invitation_id=invitation_id,
        researcher_id=current_user.researcher.id,
        accept=response_data.accept
    )
    
    return invitation


@router.post("/{program_id}/join", status_code=status.HTTP_200_OK)
@router.get("/{program_id}/join", status_code=status.HTTP_200_OK)
@router.post("/programs/{program_id}/join", status_code=status.HTTP_200_OK)
def join_program(
    program_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Join a public bug bounty program.
    
    Only researchers can join programs.
    Private programs require invitation acceptance.
    """
    if not current_user.is_researcher():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only researchers can join programs"
        )
    
    # Get researcher profile
    from src.domain.models.researcher import Researcher
    researcher = db.query(Researcher).filter(Researcher.user_id == current_user.id).first()
    
    if not researcher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Researcher profile not found. Please complete your researcher profile first."
        )
    
    service = ProgramService(db)
    
    participation = service.join_program(
        program_id=program_id,
        researcher_id=researcher.id
    )
    
    return {
        "message": "Successfully joined program",
        "program_id": str(program_id),
        "joined_at": participation.joined_at
    }


@router.post("/{program_id}/pause", response_model=ProgramResponse)
@router.get("/{program_id}/pause", response_model=ProgramResponse)
def pause_program(
    program_id: UUID,
    current_user: User = Depends(require_organization),
    db: Session = Depends(get_db)
):
    """
    Pause a program (temporarily stop accepting submissions).
    
    Only the organization that owns the program can pause it.
    Supports both GET and POST methods.
    """
    service = ProgramService(db)
    
    program = service.get_program(program_id)
    
    # Verify ownership
    if program.organization_id != current_user.organization.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to pause this program"
        )
    
    # Update status to paused
    program.status = "paused"
    updated_program = service.program_repo.update_program(program)
    
    return updated_program


@router.post("/{program_id}/resume", response_model=ProgramResponse)
@router.get("/{program_id}/resume", response_model=ProgramResponse)
def resume_program(
    program_id: UUID,
    current_user: User = Depends(require_organization),
    db: Session = Depends(get_db)
):
    """
    Resume a paused program.
    
    Only the organization that owns the program can resume it.
    Supports both GET and POST methods.
    """
    service = ProgramService(db)
    
    program = service.get_program(program_id)
    
    # Verify ownership
    if program.organization_id != current_user.organization.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to resume this program"
        )
    
    # Check if program is paused
    if program.status != "paused":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Program is not paused"
        )
    
    # Update status back to public
    program.status = "public"
    updated_program = service.program_repo.update_program(program)
    
    return updated_program


@router.post("/{program_id}/close", response_model=ProgramResponse)
@router.get("/{program_id}/close", response_model=ProgramResponse)
def close_program(
    program_id: UUID,
    current_user: User = Depends(require_organization),
    db: Session = Depends(get_db)
):
    """
    Close a program (permanently stop accepting submissions).
    
    Only the organization that owns the program can close it.
    Closed programs cannot be reopened.
    Supports both GET and POST methods.
    """
    service = ProgramService(db)
    
    program = service.get_program(program_id)
    
    # Verify ownership
    if program.organization_id != current_user.organization.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to close this program"
        )
    
    # Update status to closed
    program.status = "closed"
    program.end_date = datetime.utcnow()
    updated_program = service.program_repo.update_program(program)
    
    return updated_program


@router.post("/{program_id}/archive", response_model=ProgramResponse)
@router.get("/{program_id}/archive", response_model=ProgramResponse)
def archive_program(
    program_id: UUID,
    current_user: User = Depends(require_organization),
    db: Session = Depends(get_db)
):
    """
    Archive a program (soft delete - hide from listings but keep data).
    
    Only the organization that owns the program can archive it.
    Archived programs can be restored.
    Supports both GET and POST methods.
    """
    service = ProgramService(db)
    
    program = service.get_program(program_id)
    
    # Verify ownership
    if program.organization_id != current_user.organization.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to archive this program"
        )
    
    # Soft delete (archive)
    service.program_repo.soft_delete_program(program_id)
    
    # Refresh to get updated data
    archived_program = service.get_program(program_id)
    
    return archived_program


@router.post("/{program_id}/restore", response_model=ProgramResponse)
@router.get("/{program_id}/restore", response_model=ProgramResponse)
def restore_program(
    program_id: UUID,
    current_user: User = Depends(require_organization),
    db: Session = Depends(get_db)
):
    """
    Restore an archived program.
    
    Only the organization that owns the program can restore it.
    Supports both GET and POST methods.
    """
    service = ProgramService(db)
    
    # Get program including archived ones
    program = service.program_repo.get_program_by_id(program_id)
    
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Program not found"
        )
    
    # Verify ownership
    if program.organization_id != current_user.organization.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to restore this program"
        )
    
    # Check if program is archived
    if not program.deleted_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Program is not archived"
        )
    
    # Restore (remove deleted_at timestamp)
    program.deleted_at = None
    updated_program = service.program_repo.update_program(program)
    
    return updated_program


@router.delete("/{program_id}", status_code=status.HTTP_204_NO_CONTENT)
@router.post("/{program_id}/delete", status_code=status.HTTP_200_OK)
@router.get("/{program_id}/delete", status_code=status.HTTP_200_OK)
def delete_program(
    program_id: UUID,
    current_user: User = Depends(require_organization),
    db: Session = Depends(get_db)
):
    """
    Permanently delete a program.
    
    Only draft programs or archived programs can be permanently deleted.
    Only the organization that owns the program can delete it.
    Supports DELETE, POST, and GET methods for compatibility.
    """
    service = ProgramService(db)
    
    # Get program including archived ones
    program = service.program_repo.get_program_by_id(program_id)
    
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Program not found"
        )
    
    # Verify ownership
    if program.organization_id != current_user.organization.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this program"
        )
    
    # Only allow deletion of draft or archived programs
    if program.status not in ['draft'] and not program.deleted_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only draft or archived programs can be permanently deleted"
        )
    
    # Permanently delete
    db.delete(program)
    db.commit()
    
    return {"message": "Program deleted successfully"}
