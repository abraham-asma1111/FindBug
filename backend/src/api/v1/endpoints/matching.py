"""BountyMatch API endpoints - FREQ-16."""
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.authorization import get_current_user
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
    if current_user.role != "researcher":
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
    if current_user.role != "researcher":
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
    if current_user.role != "researcher":
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
