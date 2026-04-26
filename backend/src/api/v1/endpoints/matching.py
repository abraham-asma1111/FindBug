"""BountyMatch API endpoints - FREQ-16."""
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.dependencies import get_current_user
from src.core.role_access import is_ptaas_admin_or_staff
from src.domain.models.user import User
from src.services.matching_service import MatchingService


router = APIRouter(prefix="/matching", tags=["matching"])


@router.post("/requests")
def create_matching_request(
    engagement_type: str,
    criteria: dict,
    required_skills: Optional[List[str]] = None,
    engagement_id: Optional[UUID] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create matching request - FREQ-16.
    
    Organization creates request to match researchers.
    """
    if current_user.role != "organization":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organizations can create matching requests"
        )
    
    service = MatchingService(db)
    
    try:
        request = service.create_matching_request(
            organization_id=current_user.organization.id,
            engagement_type=engagement_type,
            criteria=criteria,
            required_skills=required_skills,
            engagement_id=engagement_id
        )
        
        return {
            "message": "Matching request created successfully",
            "request_id": str(request.id),
            "status": request.status
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create matching request: {str(e)}"
        )


@router.post("/requests/{request_id}/match")
def match_researchers(
    request_id: UUID,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Execute matching algorithm - FREQ-16.
    
    Matches researchers to request based on skills and performance.
    """
    if current_user.role not in ["organization", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organizations and admins can execute matching"
        )
    
    service = MatchingService(db)
    
    try:
        results = service.match_researchers(
            request_id=request_id,
            limit=limit
        )
        
        return {
            "message": "Matching completed successfully",
            "total_matches": len(results),
            "matches": [
                {
                    "researcher_id": str(r.researcher_id),
                    "match_score": float(r.match_score),
                    "skill_score": float(r.skill_score),
                    "reputation_score": float(r.reputation_score),
                    "rank": r.rank
                }
                for r in results
            ]
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Matching failed: {str(e)}"
        )


@router.get("/requests/{request_id}/results")
@router.post("/requests/{request_id}/results")
def get_matching_results(
    request_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get matching results - FREQ-16.
    
    View matched researchers for a request.
    """
    if current_user.role not in ["organization", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organizations and admins can view results"
        )
    
    service = MatchingService(db)
    
    results = service.get_matching_results(request_id)
    
    return {
        "request_id": str(request_id),
        "total_matches": len(results),
        "matches": [
            {
                "id": str(r.id),
                "researcher_id": str(r.researcher_id),
                "match_score": float(r.match_score),
                "skill_score": float(r.skill_score),
                "reputation_score": float(r.reputation_score),
                "rank": r.rank
            }
            for r in results
        ]
    }


@router.post("/requests/{request_id}/invite")
def send_invitations(
    request_id: UUID,
    researcher_ids: List[UUID],
    message: Optional[str] = None,
    expires_in_days: int = 7,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send invitations to researchers - FREQ-16.
    
    Organization invites matched researchers.
    """
    if current_user.role != "organization":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organizations can send invitations"
        )
    
    service = MatchingService(db)
    
    try:
        invitations = service.send_invitations(
            request_id=request_id,
            researcher_ids=researcher_ids,
            message=message,
            expires_in_days=expires_in_days
        )
        
        return {
            "message": "Invitations sent successfully",
            "total_sent": len(invitations),
            "invitations": [
                {
                    "id": str(inv.id),
                    "researcher_id": str(inv.researcher_id),
                    "match_score": float(inv.match_score),
                    "expires_at": inv.expires_at
                }
                for inv in invitations
            ]
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/invitations")
@router.post("/invitations")
def get_my_invitations(
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get researcher invitations - FREQ-16.
    
    Researcher views their invitations.
    """
    if not current_user.is_researcher():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only researchers can view invitations"
        )
    
    service = MatchingService(db)
    
    invitations = service.get_researcher_invitations(
        researcher_id=current_user.researcher.id,
        status=status_filter
    )
    
    return {
        "total": len(invitations),
        "invitations": [
            {
                "id": str(inv.id),
                "request_id": str(inv.request_id),
                "engagement_id": str(inv.engagement_id) if inv.engagement_id else None,
                "match_score": float(inv.match_score),
                "status": inv.status,
                "message": inv.message,
                "sent_at": inv.sent_at,
                "expires_at": inv.expires_at,
                "viewed_at": inv.viewed_at,
                "responded_at": inv.responded_at
            }
            for inv in invitations
        ]
    }


@router.post("/invitations/{invitation_id}/respond")
def respond_to_invitation(
    invitation_id: UUID,
    accept: bool,
    response_note: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Respond to invitation - FREQ-16.
    
    Researcher accepts or declines invitation.
    """
    if not current_user.is_researcher():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only researchers can respond to invitations"
        )
    
    service = MatchingService(db)
    
    try:
        invitation = service.respond_to_invitation(
            invitation_id=invitation_id,
            researcher_id=current_user.researcher.id,
            accept=accept,
            response_note=response_note
        )
        
        return {
            "message": f"Invitation {'accepted' if accept else 'declined'} successfully",
            "invitation_id": str(invitation.id),
            "status": invitation.status
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/recommendations")
@router.post("/recommendations")
def get_program_recommendations(
    limit: int = 5,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get program recommendations - FREQ-16.
    
    Researcher gets recommended programs based on skills.
    """
    if not current_user.is_researcher():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only researchers can get recommendations"
        )
    
    service = MatchingService(db)
    
    programs = service.get_researcher_recommendations(
        researcher_id=current_user.researcher.id,
        limit=limit
    )
    
    return {
        "total": len(programs),
        "programs": [
            {
                "id": str(p.id),
                "name": p.name,
                "description": p.description,
                "status": p.status,
                "organization_id": str(p.organization_id)
            }
            for p in programs
        ]
    }


@router.get("/organization/researchers")
def list_researchers_for_organization(
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all researchers available for assignment.
    
    Organizations use this to browse and select researchers for engagements.
    """
    if current_user.role not in ["organization", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organizations and admins can list researchers"
        )
    
    from src.domain.models.researcher import Researcher
    
    # Get all researchers with their profiles
    researchers = db.query(Researcher).limit(limit).all()
    
    return [
        {
            "id": str(r.id),
            "user": {
                "id": str(r.user.id),
                "email": r.user.email,
                "full_name": f"{r.first_name or ''} {r.last_name or ''}".strip() or r.user.email.split('@')[0],
                "username": r.username or r.user.email.split('@')[0]
            },
            "reputation_score": float(r.reputation_score) if r.reputation_score else 0,
            "total_reports": r.total_reports or 0,
            "verified_reports": r.verified_reports or 0,
            "profile": {
                "experience_years": 0,  # Not in current model
                "skills": r.skills.split(',') if r.skills else [],
                "specializations": [],  # Not in current model
                "bio": r.bio
            }
        }
        for r in researchers
    ]


@router.post("/feedback")
def submit_feedback(
    request_id: UUID,
    researcher_id: UUID,
    rating: int,
    quality_score: int,
    communication_score: int,
    timeliness_score: int,
    would_work_again: bool,
    comments: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit feedback on match - FREQ-16.
    
    Organization provides feedback on researcher.
    """
    if current_user.role != "organization":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organizations can submit feedback"
        )
    
    service = MatchingService(db)
    
    feedback = service.submit_feedback(
        request_id=request_id,
        researcher_id=researcher_id,
        organization_id=current_user.organization.id,
        rating=rating,
        quality_score=quality_score,
        communication_score=communication_score,
        timeliness_score=timeliness_score,
        would_work_again=would_work_again,
        comments=comments
    )
    
    return {
        "message": "Feedback submitted successfully",
        "feedback_id": str(feedback.id)
    }



# FREQ-32: Advanced PTaaS Matching Endpoints

@router.post("/ptaas/{engagement_id}/match")
def match_researchers_for_ptaas_engagement(
    engagement_id: int,
    team_size: int,
    auto_invite: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Match and assign researchers to PTaaS engagement - FREQ-32.
    
    Automatically finds best-matched researchers based on:
    - Skills and methodology expertise
    - Reputation and past performance
    - Vulnerability expertise
    - Availability
    """
    if current_user.role not in ["organization", "admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    service = MatchingService(db)
    
    try:
        matches = service.auto_assign_researchers_to_ptaas(
            engagement_id=engagement_id,
            team_size=team_size,
            auto_invite=auto_invite
        )
        
        return {
            "message": f"Successfully matched {len(matches)} researchers",
            "engagement_id": engagement_id,
            "team_size": len(matches),
            "matches": matches,
            "invitations_sent": auto_invite
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Matching failed: {str(e)}"
        )


@router.get("/ptaas/{engagement_id}/candidates")
def get_ptaas_engagement_candidates(
    engagement_id: int,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get candidate researchers for PTaaS engagement - FREQ-32.
    
    Returns ranked list of researchers with detailed match scores.
    """
    if current_user.role not in ["organization", "admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    service = MatchingService(db)
    
    # Get engagement
    from src.domain.models.ptaas import PTaaSEngagement
    engagement = db.query(PTaaSEngagement).filter(
        PTaaSEngagement.id == engagement_id
    ).first()
    
    if not engagement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PTaaS engagement not found"
        )
    
    # Get matches
    methodology = engagement.testing_methodology
    required_skills = engagement.scope.get('required_skills', []) if engagement.scope else []
    compliance_requirements = engagement.compliance_requirements
    
    matches = service.match_researchers_for_ptaas(
        engagement_id=engagement_id,
        methodology=methodology,
        required_skills=required_skills,
        compliance_requirements=compliance_requirements,
        team_size=engagement.team_size,
        limit=limit
    )
    
    # Format response
    candidates = []
    for researcher, match_details in matches:
        full_name = f"{researcher.first_name or ''} {researcher.last_name or ''}".strip() or researcher.user.email.split('@')[0]
        candidates.append({
            'researcher_id': str(researcher.id),
            'researcher_name': full_name,
            'reputation_score': researcher.reputation_score,
            'match_score': match_details['overall_score'],
            'skill_score': match_details['skill_score'],
            'performance_score': match_details['performance_score'],
            'expertise_score': match_details['expertise_score'],
            'availability_score': match_details['availability_score'],
            'details': match_details['details']
        })
    
    return {
        "engagement_id": engagement_id,
        "engagement_name": engagement.name,
        "methodology": methodology,
        "total_candidates": len(candidates),
        "candidates": candidates
    }


@router.get("/researcher/ptaas-recommendations")
def get_researcher_ptaas_recommendations(
    limit: int = 5,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get PTaaS engagement recommendations for researcher - FREQ-32.
    
    Returns engagements that match researcher's skills and experience.
    """
    if not current_user.is_researcher():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only researchers can access recommendations"
        )
    
    service = MatchingService(db)
    
    try:
        recommendations = service.get_researcher_ptaas_recommendations(
            researcher_id=current_user.researcher.id,
            limit=limit
        )
        
        return {
            "researcher_id": str(current_user.researcher.id),
            "total_recommendations": len(recommendations),
            "recommendations": recommendations
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get recommendations: {str(e)}"
        )


@router.get("/researcher/{researcher_id}/ptaas-score")
def get_researcher_ptaas_match_score(
    researcher_id: UUID,
    methodology: str,
    required_skills: List[str],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed PTaaS match score for specific researcher - FREQ-32.
    
    Useful for evaluating individual researchers before assignment.
    """
    if current_user.role not in ["organization", "admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    service = MatchingService(db)
    
    # Get researcher
    from src.domain.models.researcher import Researcher
    researcher = db.query(Researcher).filter(
        Researcher.id == researcher_id
    ).first()
    
    if not researcher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Researcher not found"
        )
    
    # Calculate match score
    match_details = service._calculate_ptaas_match_score(
        researcher=researcher,
        methodology=methodology,
        required_skills=required_skills,
        compliance_requirements=None
    )
    
    full_name = f"{researcher.first_name or ''} {researcher.last_name or ''}".strip() or researcher.user.email.split('@')[0]
    
    return {
        "researcher_id": str(researcher_id),
        "researcher_name": full_name,
        "methodology": methodology,
        "match_details": match_details
    }



# FREQ-33: Configuration and Approval Endpoints

@router.post("/configuration")
def create_or_update_matching_configuration(
    config_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create or update matching configuration - FREQ-33.
    
    Allows organizations to customize matching criteria:
    - Scoring weights
    - Minimum thresholds
    - Approval settings
    - Preferences
    """
    if current_user.role not in ["organization", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organizations and admins can configure matching"
        )
    
    organization_id = current_user.organization.id if current_user.role == "organization" else config_data.get("organization_id")
    
    if not organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization ID required"
        )
    
    service = MatchingService(db)
    
    try:
        config = service.create_matching_configuration(
            organization_id=UUID(str(organization_id)),
            config_data=config_data
        )
        
        return {
            "message": "Matching configuration saved successfully",
            "configuration": {
                "organization_id": str(config.organization_id),
                "skill_weight": float(config.skill_weight),
                "reputation_weight": float(config.reputation_weight),
                "performance_weight": float(config.performance_weight),
                "expertise_weight": float(config.expertise_weight),
                "availability_weight": float(config.availability_weight),
                "min_overall_score": float(config.min_overall_score),
                "min_reputation": config.min_reputation,
                "min_experience_years": config.min_experience_years,
                "require_approval": config.require_approval,
                "auto_approve_threshold": float(config.auto_approve_threshold) if config.auto_approve_threshold else None,
                "approval_timeout_hours": config.approval_timeout_hours
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save configuration: {str(e)}"
        )


@router.get("/configuration")
def get_matching_configuration(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get matching configuration for organization - FREQ-33."""
    if current_user.role not in ["organization", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    organization_id = current_user.organization.id if current_user.role == "organization" else None
    
    if not organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization ID required"
        )
    
    service = MatchingService(db)
    config = service.get_matching_configuration(UUID(str(organization_id)))
    
    if not config:
        return {
            "message": "No configuration found, using defaults",
            "configuration": None
        }
    
    return {
        "configuration": {
            "organization_id": str(config.organization_id),
            "skill_weight": float(config.skill_weight),
            "reputation_weight": float(config.reputation_weight),
            "performance_weight": float(config.performance_weight),
            "expertise_weight": float(config.expertise_weight),
            "availability_weight": float(config.availability_weight),
            "min_overall_score": float(config.min_overall_score),
            "min_reputation": config.min_reputation,
            "min_experience_years": config.min_experience_years,
            "require_approval": config.require_approval,
            "auto_approve_threshold": float(config.auto_approve_threshold) if config.auto_approve_threshold else None,
            "approval_timeout_hours": config.approval_timeout_hours,
            "preferred_timezones": config.preferred_timezones,
            "excluded_researchers": config.excluded_researchers,
            "preferred_researchers": config.preferred_researchers
        }
    }


@router.post("/assignments/propose")
def propose_researcher_assignment(
    engagement_id: int,
    engagement_type: str,
    researcher_id: UUID,
    match_score: float,
    match_details: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Propose researcher assignment for approval - FREQ-33.
    
    Creates assignment proposal that may require approval.
    """
    if current_user.role not in ["organization", "admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    organization_id = current_user.organization.id if current_user.role == "organization" else match_details.get("organization_id")
    
    if not organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization ID required"
        )
    
    service = MatchingService(db)
    
    try:
        assignment = service.propose_researcher_assignment(
            engagement_id=engagement_id,
            engagement_type=engagement_type,
            researcher_id=researcher_id,
            organization_id=UUID(str(organization_id)),
            match_score=match_score,
            match_details=match_details,
            proposed_by=current_user.id
        )
        
        return {
            "message": "Assignment proposed successfully",
            "assignment": {
                "id": str(assignment.id),
                "engagement_id": assignment.engagement_id,
                "researcher_id": str(assignment.researcher_id),
                "match_score": float(assignment.match_score),
                "status": assignment.status,
                "expires_at": assignment.expires_at.isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to propose assignment: {str(e)}"
        )


@router.post("/assignments/{assignment_id}/approve")
def approve_assignment(
    assignment_id: UUID,
    notes: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Approve researcher assignment - FREQ-33.
    
    Organization or admin approves proposed assignment.
    """
    if current_user.role not in ["organization", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organizations and admins can approve assignments"
        )
    
    service = MatchingService(db)
    
    try:
        assignment = service.approve_researcher_assignment(
            assignment_id=assignment_id,
            approved_by=current_user.id,
            notes=notes
        )
        
        return {
            "message": "Assignment approved successfully",
            "assignment": {
                "id": str(assignment.id),
                "engagement_id": assignment.engagement_id,
                "researcher_id": str(assignment.researcher_id),
                "status": assignment.status,
                "reviewed_at": assignment.reviewed_at.isoformat() if assignment.reviewed_at else None
            }
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to approve assignment: {str(e)}"
        )


@router.post("/assignments/{assignment_id}/reject")
def reject_assignment(
    assignment_id: UUID,
    reason: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Reject researcher assignment - FREQ-33.
    
    Organization or admin rejects proposed assignment.
    """
    if current_user.role not in ["organization", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organizations and admins can reject assignments"
        )
    
    service = MatchingService(db)
    
    try:
        assignment = service.reject_researcher_assignment(
            assignment_id=assignment_id,
            rejected_by=current_user.id,
            reason=reason
        )
        
        return {
            "message": "Assignment rejected successfully",
            "assignment": {
                "id": str(assignment.id),
                "engagement_id": assignment.engagement_id,
                "researcher_id": str(assignment.researcher_id),
                "status": assignment.status,
                "reviewed_at": assignment.reviewed_at.isoformat() if assignment.reviewed_at else None,
                "review_notes": assignment.review_notes
            }
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reject assignment: {str(e)}"
        )


@router.get("/assignments/pending")
def get_pending_assignments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get pending assignments for organization - FREQ-33.
    
    Returns assignments awaiting approval.
    """
    if current_user.role not in ["organization", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    organization_id = current_user.organization.id if current_user.role == "organization" else None
    
    if not organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization ID required"
        )
    
    service = MatchingService(db)
    assignments = service.get_pending_assignments(UUID(str(organization_id)))
    
    return {
        "total_pending": len(assignments),
        "assignments": [
            {
                "id": str(a.id),
                "engagement_id": a.engagement_id,
                "engagement_type": a.engagement_type,
                "researcher_id": str(a.researcher_id),
                "researcher_name": f"{a.researcher.first_name or ''} {a.researcher.last_name or ''}".strip() or a.researcher.user.email.split('@')[0],
                "match_score": float(a.match_score),
                "match_details": a.match_details,
                "proposed_at": a.proposed_at.isoformat(),
                "expires_at": a.expires_at.isoformat()
            }
            for a in assignments
        ]
    }


@router.post("/assignments/bulk-approve")
def bulk_approve_assignments(
    assignment_ids: List[UUID],
    notes: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Bulk approve multiple assignments - FREQ-33.
    
    Useful for approving entire teams at once.
    """
    if current_user.role not in ["organization", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organizations and admins can approve assignments"
        )
    
    service = MatchingService(db)
    
    try:
        approved = service.bulk_approve_assignments(
            assignment_ids=assignment_ids,
            approved_by=current_user.id,
            notes=notes
        )
        
        return {
            "message": f"Successfully approved {len(approved)} assignments",
            "approved_count": len(approved),
            "failed_count": len(assignment_ids) - len(approved),
            "assignments": [
                {
                    "id": str(a.id),
                    "engagement_id": a.engagement_id,
                    "researcher_id": str(a.researcher_id),
                    "status": a.status
                }
                for a in approved
            ]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to bulk approve: {str(e)}"
        )


@router.get("/assignments/{assignment_id}")
def get_assignment_details(
    assignment_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get assignment details - FREQ-33."""
    if current_user.role not in ["organization", "admin", "researcher"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    service = MatchingService(db)
    assignment = service.get_assignment_by_id(assignment_id)
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    full_name = f"{assignment.researcher.first_name or ''} {assignment.researcher.last_name or ''}".strip() or assignment.researcher.user.email.split('@')[0]
    
    return {
        "assignment": {
            "id": str(assignment.id),
            "engagement_id": assignment.engagement_id,
            "engagement_type": assignment.engagement_type,
            "researcher_id": str(assignment.researcher_id),
            "researcher_name": full_name,
            "organization_id": str(assignment.organization_id),
            "match_score": float(assignment.match_score),
            "match_details": assignment.match_details,
            "status": assignment.status,
            "proposed_at": assignment.proposed_at.isoformat(),
            "reviewed_at": assignment.reviewed_at.isoformat() if assignment.reviewed_at else None,
            "review_notes": assignment.review_notes,
            "expires_at": assignment.expires_at.isoformat()
        }
    }


# FREQ-39: Personalized Recommendations for Researchers
@router.get("/recommendations/personalized")
def get_personalized_recommendations(
    include_bug_bounty: bool = True,
    include_ptaas: bool = True,
    limit_per_type: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get personalized recommendations for researcher - FREQ-39.
    
    Provides:
    - Active bug bounty programs matching researcher profile
    - PTaaS opportunities matching expertise
    - Match scores and reasons
    - Difficulty levels and estimated compensation
    """
    # Only researchers can get recommendations
    if current_user.role != "RESEARCHER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only researchers can access recommendations"
        )
    
    service = MatchingService(db)
    return service.get_personalized_recommendations(
        current_user.id,
        include_bug_bounty,
        include_ptaas,
        limit_per_type
    )


@router.get("/recommendations/bug-bounty")
def get_bug_bounty_recommendations(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get bug bounty program recommendations - FREQ-39.
    
    Returns active programs matching researcher's skills and experience.
    """
    if current_user.role != "RESEARCHER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only researchers can access recommendations"
        )
    
    service = MatchingService(db)
    recommendations = service.get_personalized_recommendations(
        current_user.id,
        include_bug_bounty=True,
        include_ptaas=False,
        limit_per_type=limit
    )
    
    return {
        'programs': recommendations['bug_bounty_programs'],
        'total': len(recommendations['bug_bounty_programs']),
        'researcher_profile': {
            'skills': recommendations['summary'].get('researcher_skills', []),
            'reputation': recommendations['summary'].get('researcher_reputation', 0)
        }
    }


@router.get("/recommendations/ptaas")
def get_ptaas_recommendations(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get PTaaS opportunity recommendations - FREQ-39.
    
    Returns available PTaaS engagements matching researcher's expertise.
    """
    if current_user.role != "RESEARCHER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only researchers can access recommendations"
        )
    
    service = MatchingService(db)
    recommendations = service.get_personalized_recommendations(
        current_user.id,
        include_bug_bounty=False,
        include_ptaas=True,
        limit_per_type=limit
    )
    
    return {
        'opportunities': recommendations['ptaas_opportunities'],
        'total': len(recommendations['ptaas_opportunities']),
        'researcher_profile': {
            'skills': recommendations['summary'].get('researcher_skills', []),
            'reputation': recommendations['summary'].get('researcher_reputation', 0)
        }
    }


# FREQ-40: BountyMatch Performance Metrics
from datetime import datetime, timedelta

@router.get("/metrics/performance")
def get_matching_performance_metrics(
    organization_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get BountyMatch performance metrics - FREQ-40.
    
    Available to:
    - Platform admins (all data)
    - Organization members (their organization data)
    
    Metrics include:
    - Match success rate
    - Researcher acceptance rate
    - Average match scores
    - Time to assignment
    - Trends over time
    """
    # Access control
    if not is_ptaas_admin_or_staff(current_user):
        # Non-admin users can only see their organization's metrics
        if not current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        organization_id = current_user.organization_id
    
    # Parse dates
    start_dt = datetime.fromisoformat(start_date) if start_date else None
    end_dt = datetime.fromisoformat(end_date) if end_date else None
    
    service = MatchingService(db)
    return service.get_matching_performance_metrics(
        organization_id,
        start_dt,
        end_dt
    )


@router.get("/metrics/organization/{organization_id}")
def get_organization_matching_stats(
    organization_id: int,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get matching statistics for organization - FREQ-40.
    
    Shows organization-specific matching performance.
    """
    # Access control
    if not is_ptaas_admin_or_staff(current_user):
        if current_user.organization_id != organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    # Parse dates
    start_dt = datetime.fromisoformat(start_date) if start_date else None
    end_dt = datetime.fromisoformat(end_date) if end_date else None
    
    service = MatchingService(db)
    return service.get_organization_matching_stats(
        organization_id,
        start_dt,
        end_dt
    )


@router.get("/metrics/researcher/{researcher_id}")
def get_researcher_matching_stats(
    researcher_id: int,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get matching statistics for researcher - FREQ-40.
    
    Shows how well researcher is being matched to opportunities.
    """
    # Access control
    if not is_ptaas_admin_or_staff(current_user):
        if current_user.id != researcher_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    # Parse dates
    start_dt = datetime.fromisoformat(start_date) if start_date else None
    end_dt = datetime.fromisoformat(end_date) if end_date else None
    
    service = MatchingService(db)
    return service.get_researcher_matching_stats(
        researcher_id,
        start_dt,
        end_dt
    )


@router.get("/metrics/dashboard")
def get_matching_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get comprehensive matching dashboard - FREQ-40.
    
    Provides overview of matching system performance.
    Available to admins and organization members.
    """
    service = MatchingService(db)
    
    # Determine scope based on user role
    organization_id = None
    if not is_ptaas_admin_or_staff(current_user):
        if not current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        organization_id = current_user.organization_id
    
    # Get metrics for different time periods
    now = datetime.utcnow()
    
    # Last 7 days
    last_week = service.get_matching_performance_metrics(
        organization_id,
        now - timedelta(days=7),
        now
    )
    
    # Last 30 days
    last_month = service.get_matching_performance_metrics(
        organization_id,
        now - timedelta(days=30),
        now
    )
    
    # Last 90 days
    last_quarter = service.get_matching_performance_metrics(
        organization_id,
        now - timedelta(days=90),
        now
    )
    
    return {
        'dashboard_generated_at': now.isoformat(),
        'organization_id': organization_id,
        'is_platform_admin': is_ptaas_admin_or_staff(current_user),
        'periods': {
            'last_7_days': last_week,
            'last_30_days': last_month,
            'last_90_days': last_quarter
        },
        'summary': {
            'current_success_rate': last_month['success_metrics']['match_success_rate'],
            'current_acceptance_rate': last_month['success_metrics']['researcher_acceptance_rate'],
            'trend': last_month['trends']['trend_direction'],
            'total_assignments_this_month': last_month['overview']['total_assignments']
        }
    }


# ============================================
# ORGANIZATION RESEARCHER LISTING
# ============================================

@router.get("/organization/researchers")
def get_researchers_for_organization(
    search: Optional[str] = None,
    min_reputation: Optional[int] = None,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all researchers for organization to browse and invite.
    
    This endpoint is used by the researcher management page.
    Organizations can search, filter, and view all active researchers.
    """
    if current_user.role != "organization":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organizations can access this endpoint"
        )
    
    from src.domain.models.researcher import Researcher
    from src.domain.models.user import User as UserModel
    from src.domain.models.matching import ResearcherProfile
    from sqlalchemy import func, or_
    
    # Query all active researchers
    query = db.query(Researcher).join(
        UserModel,
        Researcher.user_id == UserModel.id
    ).outerjoin(
        ResearcherProfile,
        Researcher.id == ResearcherProfile.researcher_id
    ).filter(
        Researcher.is_active == True
    )
    
    # Apply search filter
    if search:
        search_term = f"%{search.lower()}%"
        query = query.filter(
            func.lower(UserModel.email).like(search_term)
        )
    
    # Apply reputation filter
    if min_reputation:
        query = query.filter(Researcher.reputation_score >= min_reputation)
    
    researchers = query.limit(limit).all()
    
    # Format response
    result = []
    for researcher in researchers:
        profile_data = None
        # Check if researcher has a profile (backref creates a single object, not a list)
        if hasattr(researcher, 'profile') and researcher.profile:
            profile = researcher.profile
            profile_data = {
                'experience_years': profile.experience_years if hasattr(profile, 'experience_years') else 0,
                'skills': profile.skills if hasattr(profile, 'skills') and profile.skills else [],
                'specializations': profile.specializations if hasattr(profile, 'specializations') and profile.specializations else [],
                'bio': researcher.bio  # Bio is on Researcher model, not profile
            }
        else:
            # If no profile, use researcher's own fields
            profile_data = {
                'experience_years': 0,
                'skills': [],
                'specializations': [],
                'bio': researcher.bio
            }
        
        result.append({
            'id': str(researcher.id),
            'user': {
                'username': researcher.user.email.split('@')[0],  # Use email prefix as username
                'email': researcher.user.email
            },
            'reputation_score': researcher.reputation_score,
            'total_reports': researcher.total_reports,
            'verified_reports': researcher.verified_reports,
            'profile': profile_data
        })
    
    return result
