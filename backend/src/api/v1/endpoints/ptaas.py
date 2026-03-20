"""
PTaaS API Endpoints
Implements FREQ-29, FREQ-30, FREQ-31
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from backend.src.core.database import get_db
from backend.src.api.v1.middlewares.auth import get_current_user
from backend.src.services.ptaas_service import PTaaSService
from backend.src.api.v1.schemas.ptaas import (
    PTaaSEngagementCreate,
    PTaaSEngagementUpdate,
    PTaaSEngagementResponse,
    PTaaSFindingCreate,
    PTaaSFindingUpdate,
    PTaaSFindingResponse,
    PTaaSDeliverableCreate,
    PTaaSDeliverableResponse,
    PTaaSProgressUpdateCreate,
    PTaaSProgressUpdateResponse
)
from backend.src.domain.models.user import User

router = APIRouter(prefix="/ptaas", tags=["PTaaS"])


# Engagement Endpoints
@router.post("/engagements", response_model=PTaaSEngagementResponse, status_code=status.HTTP_201_CREATED)
def create_engagement(
    engagement: PTaaSEngagementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create new PTaaS engagement - FREQ-29
    Only organization members can create engagements
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organization members can create PTaaS engagements"
        )
    
    service = PTaaSService(db)
    return service.create_engagement(
        organization_id=current_user.organization_id,
        engagement_data=engagement.dict(),
        created_by=current_user.id
    )


@router.get("/engagements/{engagement_id}", response_model=PTaaSEngagementResponse)
def get_engagement(
    engagement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get engagement by ID"""
    service = PTaaSService(db)
    engagement = service.get_engagement(engagement_id)
    
    if not engagement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Engagement not found"
        )
    
    # Check access
    if engagement.organization_id != current_user.organization_id:
        if not (current_user.role in ["ADMIN", "STAFF"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    return engagement


@router.get("/engagements", response_model=List[PTaaSEngagementResponse])
def list_engagements(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List engagements for current organization"""
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organization members can view engagements"
        )
    
    service = PTaaSService(db)
    return service.get_organization_engagements(current_user.organization_id)


@router.patch("/engagements/{engagement_id}", response_model=PTaaSEngagementResponse)
def update_engagement(
    engagement_id: int,
    engagement_update: PTaaSEngagementUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update engagement - FREQ-30"""
    service = PTaaSService(db)
    engagement = service.get_engagement(engagement_id)
    
    if not engagement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Engagement not found"
        )
    
    # Check access
    if engagement.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    update_data = engagement_update.dict(exclude_unset=True)
    return service.update_engagement(engagement_id, update_data, current_user.id)


@router.post("/engagements/{engagement_id}/assign", response_model=PTaaSEngagementResponse)
def assign_researchers(
    engagement_id: int,
    researcher_ids: List[int],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Assign researchers to engagement"""
    service = PTaaSService(db)
    engagement = service.get_engagement(engagement_id)
    
    if not engagement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Engagement not found"
        )
    
    # Only org members or staff can assign
    if engagement.organization_id != current_user.organization_id:
        if current_user.role not in ["ADMIN", "STAFF"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    return service.assign_researchers(engagement_id, researcher_ids, current_user.id)


@router.post("/engagements/{engagement_id}/start", response_model=PTaaSEngagementResponse)
def start_engagement(
    engagement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Start engagement"""
    service = PTaaSService(db)
    engagement = service.get_engagement(engagement_id)
    
    if not engagement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Engagement not found"
        )
    
    return service.start_engagement(engagement_id, current_user.id)


@router.post("/engagements/{engagement_id}/complete", response_model=PTaaSEngagementResponse)
def complete_engagement(
    engagement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Complete engagement"""
    service = PTaaSService(db)
    engagement = service.get_engagement(engagement_id)
    
    if not engagement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Engagement not found"
        )
    
    return service.complete_engagement(engagement_id, current_user.id)


# Finding Endpoints
@router.post("/findings", response_model=PTaaSFindingResponse, status_code=status.HTTP_201_CREATED)
def create_finding(
    finding: PTaaSFindingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new finding"""
    service = PTaaSService(db)
    
    # Verify engagement exists and user has access
    engagement = service.get_engagement(finding.engagement_id)
    if not engagement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Engagement not found"
        )
    
    return service.create_finding(finding.dict(), current_user.id)


@router.get("/engagements/{engagement_id}/findings", response_model=List[PTaaSFindingResponse])
def list_findings(
    engagement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List findings for engagement"""
    service = PTaaSService(db)
    
    # Verify access
    engagement = service.get_engagement(engagement_id)
    if not engagement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Engagement not found"
        )
    
    return service.get_engagement_findings(engagement_id)


@router.patch("/findings/{finding_id}", response_model=PTaaSFindingResponse)
def update_finding(
    finding_id: int,
    finding_update: PTaaSFindingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update finding"""
    service = PTaaSService(db)
    update_data = finding_update.dict(exclude_unset=True)
    
    finding = service.update_finding(finding_id, update_data, current_user.id)
    if not finding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Finding not found"
        )
    
    return finding


# Deliverable Endpoints
@router.post("/deliverables", response_model=PTaaSDeliverableResponse, status_code=status.HTTP_201_CREATED)
def submit_deliverable(
    deliverable: PTaaSDeliverableCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit deliverable"""
    service = PTaaSService(db)
    
    # Verify engagement exists
    engagement = service.get_engagement(deliverable.engagement_id)
    if not engagement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Engagement not found"
        )
    
    return service.submit_deliverable(deliverable.dict(), current_user.id)


@router.get("/engagements/{engagement_id}/deliverables", response_model=List[PTaaSDeliverableResponse])
def list_deliverables(
    engagement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List deliverables for engagement"""
    service = PTaaSService(db)
    
    # Verify access
    engagement = service.get_engagement(engagement_id)
    if not engagement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Engagement not found"
        )
    
    return service.get_engagement_deliverables(engagement_id)


@router.post("/deliverables/{deliverable_id}/approve", response_model=PTaaSDeliverableResponse)
def approve_deliverable(
    deliverable_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Approve deliverable"""
    service = PTaaSService(db)
    
    deliverable = service.approve_deliverable(deliverable_id, current_user.id)
    if not deliverable:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deliverable not found"
        )
    
    return deliverable


# Progress Update Endpoints
@router.post("/progress", response_model=PTaaSProgressUpdateResponse, status_code=status.HTTP_201_CREATED)
def add_progress_update(
    progress: PTaaSProgressUpdateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add progress update"""
    service = PTaaSService(db)
    
    # Verify engagement exists
    engagement = service.get_engagement(progress.engagement_id)
    if not engagement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Engagement not found"
        )
    
    return service.add_progress_update(progress.dict(), current_user.id)


@router.get("/engagements/{engagement_id}/progress", response_model=List[PTaaSProgressUpdateResponse])
def list_progress_updates(
    engagement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List progress updates for engagement"""
    service = PTaaSService(db)
    
    # Verify access
    engagement = service.get_engagement(engagement_id)
    if not engagement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Engagement not found"
        )
    
    return service.get_engagement_progress(engagement_id)


@router.get("/engagements/{engagement_id}/subscription-renewal")
def get_subscription_renewal(
    engagement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get subscription renewal information - FREQ-31"""
    service = PTaaSService(db)
    
    engagement = service.get_engagement(engagement_id)
    if not engagement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Engagement not found"
        )
    
    if engagement.pricing_model != 'SUBSCRIPTION':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Engagement is not subscription-based"
        )
    
    return service.calculate_subscription_renewal(engagement)
