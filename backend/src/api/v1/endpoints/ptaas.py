"""
PTaaS API Endpoints
Implements FREQ-29, FREQ-30, FREQ-31
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from src.core.database import get_db
from src.core.role_access import is_ptaas_admin_or_staff
from src.api.v1.middlewares.auth import get_current_user
from src.services.ptaas_service import PTaaSService
from src.api.v1.schemas.ptaas import (
    PTaaSEngagementCreate,
    PTaaSEngagementUpdate,
    PTaaSEngagementResponse,
    PTaaSFindingCreate,
    PTaaSFindingUpdate,
    PTaaSFindingResponse,
    PTaaSFindingValidation,
    PTaaSDeliverableCreate,
    PTaaSDeliverableResponse,
    PTaaSProgressUpdateCreate,
    PTaaSProgressUpdateResponse
)
from src.domain.models.user import User

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
    if not current_user.organization:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organization members can create PTaaS engagements"
        )
    
    service = PTaaSService(db)
    return service.create_engagement(
        organization_id=current_user.organization.id,
        engagement_data=engagement.dict(),
        created_by=current_user.id
    )


@router.get("/engagements/{engagement_id}", response_model=PTaaSEngagementResponse)
def get_engagement(
    engagement_id: UUID,
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
    org_id = current_user.organization.id if current_user.organization else None
    if engagement.organization_id != org_id:
        if not is_ptaas_admin_or_staff(current_user):
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
    if not current_user.organization:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organization members can view engagements"
        )
    
    service = PTaaSService(db)
    return service.get_organization_engagements(current_user.organization.id)


@router.patch("/engagements/{engagement_id}", response_model=PTaaSEngagementResponse)
def update_engagement(
    engagement_id: UUID,
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
    org_id = current_user.organization.id if current_user.organization else None
    if engagement.organization_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    update_data = engagement_update.dict(exclude_unset=True)
    return service.update_engagement(engagement_id, update_data, current_user.id)


from pydantic import BaseModel

class ResearcherAssignmentRequest(BaseModel):
    researcher_ids: List[UUID]

@router.post("/engagements/{engagement_id}/assign", response_model=PTaaSEngagementResponse)
def assign_researchers(
    engagement_id: UUID,
    request: ResearcherAssignmentRequest,
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
    org_id = current_user.organization.id if current_user.organization else None
    if engagement.organization_id != org_id:
        if not is_ptaas_admin_or_staff(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    return service.assign_researchers(engagement_id, request.researcher_ids, current_user.id)


@router.post("/engagements/{engagement_id}/start", response_model=PTaaSEngagementResponse)
def start_engagement(
    engagement_id: UUID,
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
    engagement_id: UUID,
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
    engagement_id: UUID,
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


@router.get("/findings/{finding_id}", response_model=PTaaSFindingResponse)
def get_finding(
    finding_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a single finding by ID"""
    service = PTaaSService(db)
    
    finding = service.get_finding(finding_id)
    if not finding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Finding not found"
        )
    
    return finding


@router.patch("/findings/{finding_id}", response_model=PTaaSFindingResponse)
def update_finding(
    finding_id: UUID,
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


@router.post("/findings/{finding_id}/validate", response_model=PTaaSFindingResponse)
def validate_finding(
    finding_id: UUID,
    validation: PTaaSFindingValidation,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Validate a finding - FREQ-35
    Marks finding as validated and optionally requires retest
    """
    service = PTaaSService(db)
    
    # Only staff or org members can validate
    if not is_ptaas_admin_or_staff(current_user):
        # Check if user is from the engagement's organization
        finding = service.get_finding(finding_id)
        if not finding:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Finding not found"
            )
        
        engagement = service.get_engagement(finding.engagement_id)
        org_id = current_user.organization.id if current_user.organization else None
        if engagement.organization_id != org_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    return service.validate_finding(
        finding_id,
        current_user.id,
        validation.validated,
        validation.retest_required,
        validation.retest_notes
    )


@router.get("/findings/template")
def get_finding_template(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get structured finding template - FREQ-35
    Returns template with all mandatory fields and requirements
    """
    service = PTaaSService(db)
    return service.get_finding_template()


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
    engagement_id: UUID,
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
    deliverable_id: UUID,
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
    engagement_id: UUID,
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
    engagement_id: UUID,
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


# Dashboard Endpoints - FREQ-34
from src.services.ptaas_dashboard_service import PTaaSDashboardService
from src.domain.models.ptaas_dashboard import PTaaSTestingPhase
from src.api.v1.schemas.ptaas_dashboard import (
    PTaaSTestingPhaseCreate,
    PTaaSTestingPhaseUpdate,
    PTaaSTestingPhaseResponse,
    PTaaSChecklistItemCreate,
    PTaaSChecklistItemComplete,
    PTaaSChecklistItemResponse,
    PTaaSCollaborationUpdateCreate,
    PTaaSCollaborationUpdateResponse,
    PTaaSMilestoneCreate,
    PTaaSMilestoneUpdate,
    PTaaSMilestoneResponse,
    PTaaSDashboardResponse
)


@router.get("/engagements/{engagement_id}/dashboard", response_model=PTaaSDashboardResponse)
def get_engagement_dashboard(
    engagement_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get comprehensive dashboard for engagement - FREQ-34
    Shows testing phases, methodology checklists, findings, and collaboration updates
    """
    ptaas_service = PTaaSService(db)
    engagement = ptaas_service.get_engagement(engagement_id)
    
    if not engagement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Engagement not found"
        )
    
    # Check access - allow organization members, assigned researchers, or admin/staff
    org_id = current_user.organization.id if current_user.organization else None
    is_assigned_researcher = str(current_user.id) in engagement.assigned_researchers if engagement.assigned_researchers else False
    
    if engagement.organization_id != org_id and not is_assigned_researcher:
        if not is_ptaas_admin_or_staff(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    dashboard_service = PTaaSDashboardService(db)
    return dashboard_service.get_engagement_dashboard(engagement_id)


@router.post("/engagements/{engagement_id}/initialize-phases", response_model=List[PTaaSTestingPhaseResponse])
def initialize_engagement_phases(
    engagement_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Initialize testing phases based on methodology - FREQ-34
    Auto-creates phases for OWASP, PTES, or NIST methodologies
    """
    ptaas_service = PTaaSService(db)
    engagement = ptaas_service.get_engagement(engagement_id)
    
    if not engagement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Engagement not found"
        )
    
    # Check access - allow organization members, assigned researchers, or admin/staff
    org_id = current_user.organization.id if current_user.organization else None
    is_assigned_researcher = str(current_user.id) in engagement.assigned_researchers if engagement.assigned_researchers else False
    
    if engagement.organization_id != org_id and not is_assigned_researcher:
        if not is_ptaas_admin_or_staff(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    dashboard_service = PTaaSDashboardService(db)
    return dashboard_service.initialize_engagement_phases(
        engagement_id, 
        engagement.testing_methodology
    )


# Testing Phase Endpoints
@router.post("/phases", response_model=PTaaSTestingPhaseResponse, status_code=status.HTTP_201_CREATED)
def create_testing_phase(
    phase: PTaaSTestingPhaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create testing phase - FREQ-34"""
    dashboard_service = PTaaSDashboardService(db)
    return dashboard_service.create_testing_phase(phase.dict())


@router.patch("/phases/{phase_id}", response_model=PTaaSTestingPhaseResponse)
def update_testing_phase(
    phase_id: UUID,
    phase_update: PTaaSTestingPhaseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update testing phase - FREQ-34"""
    dashboard_service = PTaaSDashboardService(db)
    update_data = phase_update.dict(exclude_unset=True)
    
    if 'progress_percentage' in update_data:
        return dashboard_service.update_phase_progress(
            phase_id, 
            update_data['progress_percentage'],
            update_data.get('status')
        )
    
    phase = dashboard_service.db.query(PTaaSTestingPhase).filter(
        PTaaSTestingPhase.id == phase_id
    ).first()
    
    if not phase:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Phase not found"
        )
    
    for key, value in update_data.items():
        setattr(phase, key, value)
    
    dashboard_service.db.commit()
    dashboard_service.db.refresh(phase)
    return phase


# Checklist Endpoints
@router.post("/checklist", response_model=PTaaSChecklistItemResponse, status_code=status.HTTP_201_CREATED)
def create_checklist_item(
    item: PTaaSChecklistItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create checklist item - FREQ-34"""
    dashboard_service = PTaaSDashboardService(db)
    return dashboard_service.create_checklist_item(item.dict())


@router.get("/phases/{phase_id}/checklist", response_model=List[PTaaSChecklistItemResponse])
def get_phase_checklist(
    phase_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get checklist for phase - FREQ-34"""
    dashboard_service = PTaaSDashboardService(db)
    return dashboard_service.get_phase_checklist(phase_id)


@router.post("/checklist/{item_id}/complete", response_model=PTaaSChecklistItemResponse)
def complete_checklist_item(
    item_id: UUID,
    completion: PTaaSChecklistItemComplete,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark checklist item as complete - FREQ-34"""
    dashboard_service = PTaaSDashboardService(db)
    return dashboard_service.complete_checklist_item(
        item_id,
        current_user.id,
        completion.notes
    )


# Collaboration Endpoints
@router.post("/collaboration", response_model=PTaaSCollaborationUpdateResponse, status_code=status.HTTP_201_CREATED)
def add_collaboration_update(
    update: PTaaSCollaborationUpdateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add collaboration update - FREQ-34"""
    dashboard_service = PTaaSDashboardService(db)
    update_data = update.dict()
    update_data['created_by'] = current_user.id
    return dashboard_service.add_collaboration_update(update_data)


@router.get("/engagements/{engagement_id}/collaboration", response_model=List[PTaaSCollaborationUpdateResponse])
def get_collaboration_updates(
    engagement_id: UUID,
    update_type: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get collaboration updates - FREQ-34"""
    dashboard_service = PTaaSDashboardService(db)
    return dashboard_service.get_collaboration_updates(engagement_id, update_type, limit)


@router.post("/collaboration/{update_id}/pin", response_model=PTaaSCollaborationUpdateResponse)
def pin_collaboration_update(
    update_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Pin collaboration update - FREQ-34"""
    dashboard_service = PTaaSDashboardService(db)
    return dashboard_service.pin_update(update_id)


# Milestone Endpoints
@router.post("/milestones", response_model=PTaaSMilestoneResponse, status_code=status.HTTP_201_CREATED)
def create_milestone(
    milestone: PTaaSMilestoneCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create milestone - FREQ-34"""
    dashboard_service = PTaaSDashboardService(db)
    return dashboard_service.create_milestone(milestone.dict())


@router.get("/engagements/{engagement_id}/milestones", response_model=List[PTaaSMilestoneResponse])
def get_engagement_milestones(
    engagement_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get milestones for engagement - FREQ-34"""
    dashboard_service = PTaaSDashboardService(db)
    return dashboard_service.get_engagement_milestones(engagement_id)


@router.post("/milestones/{milestone_id}/complete", response_model=PTaaSMilestoneResponse)
def complete_milestone(
    milestone_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark milestone as complete - FREQ-34"""
    dashboard_service = PTaaSDashboardService(db)
    return dashboard_service.complete_milestone(milestone_id)


# Triage Endpoints - FREQ-36
from src.services.ptaas_triage_service import PTaaSTriageService
from src.api.v1.schemas.ptaas_triage import (
    PTaaSFindingTriageCreate,
    PTaaSFindingTriageResponse,
    PTaaSFindingPrioritizationCreate,
    PTaaSFindingPrioritizationResponse,
    PTaaSExecutiveReportCreate,
    PTaaSExecutiveReportResponse,
    PTaaSPendingTriageResponse
)


@router.post("/findings/{finding_id}/triage", response_model=PTaaSFindingTriageResponse, status_code=status.HTTP_201_CREATED)
def triage_finding(
    finding_id: UUID,
    triage_data: PTaaSFindingTriageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Triage and validate a finding - FREQ-36
    Only platform triage specialists (STAFF/ADMIN) can triage
    """
    if not is_ptaas_admin_or_staff(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only triage specialists can triage findings"
        )
    
    triage_service = PTaaSTriageService(db)
    return triage_service.triage_finding(
        finding_id,
        current_user.id,
        triage_data.dict()
    )


@router.get("/findings/{finding_id}/triage", response_model=PTaaSFindingTriageResponse)
def get_finding_triage(
    finding_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get triage record for finding - FREQ-36"""
    triage_service = PTaaSTriageService(db)
    triage = triage_service.get_finding_triage(finding_id)
    
    if not triage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Triage record not found"
        )
    
    return triage


@router.get("/triage/pending", response_model=List[PTaaSPendingTriageResponse])
def get_pending_triage(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get findings pending triage - FREQ-36
    Only triage specialists can access
    """
    if not is_ptaas_admin_or_staff(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only triage specialists can view pending triage"
        )
    
    triage_service = PTaaSTriageService(db)
    return triage_service.get_pending_triage(limit)


@router.get("/triage/queue", response_model=List[PTaaSPendingTriageResponse])
def get_triage_queue(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get triage queue (alias for /triage/pending) - FREQ-35
    Only triage specialists can access
    """
    if not is_ptaas_admin_or_staff(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only triage specialists can view triage queue"
        )
    
    triage_service = PTaaSTriageService(db)
    return triage_service.get_pending_triage(limit)


@router.get("/dashboard")
def get_ptaas_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get PTaaS dashboard overview - FREQ-30
    
    Shows:
    - Active engagements
    - Pending findings
    - Recent activity
    - Statistics
    """
    service = PTaaSService(db)
    
    # Get user's engagements based on role
    if current_user.is_organization():
        if not current_user.organization:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Organization profile not found"
            )
        engagements = service.get_organization_engagements(current_user.organization.id)
    elif is_ptaas_admin_or_staff(current_user):
        # Staff can see all engagements
        engagements = db.query(service.db.query(PTaaSService).all())
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Calculate statistics
    total_engagements = len(engagements) if engagements else 0
    active_engagements = len([e for e in engagements if e.status == 'active']) if engagements else 0
    
    return {
        "total_engagements": total_engagements,
        "active_engagements": active_engagements,
        "engagements": engagements[:5] if engagements else []  # Return first 5
    }


@router.post("/findings/{finding_id}/prioritize", response_model=PTaaSFindingPrioritizationResponse, status_code=status.HTTP_201_CREATED)
def prioritize_finding(
    finding_id: UUID,
    prioritization: PTaaSFindingPrioritizationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Prioritize a finding - FREQ-36
    Triage specialists can adjust priority with justification
    """
    if not is_ptaas_admin_or_staff(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only triage specialists can prioritize findings"
        )
    
    triage_service = PTaaSTriageService(db)
    return triage_service.prioritize_finding(
        finding_id,
        current_user.id,
        prioritization.new_priority,
        prioritization.reason,
        prioritization.factors_considered
    )


@router.post("/engagements/{engagement_id}/executive-report", response_model=PTaaSExecutiveReportResponse, status_code=status.HTTP_201_CREATED)
def generate_executive_report(
    engagement_id: UUID,
    report_data: PTaaSExecutiveReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate compliance-ready executive report - FREQ-36
    Includes risk ratings, evidence summary, and recommendations
    """
    if not is_ptaas_admin_or_staff(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only triage specialists can generate executive reports"
        )
    
    triage_service = PTaaSTriageService(db)
    return triage_service.generate_executive_report(
        engagement_id,
        current_user.id,
        report_data.dict()
    )


@router.get("/executive-reports/{report_id}", response_model=PTaaSExecutiveReportResponse)
def get_executive_report(
    report_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get executive report by ID - FREQ-36"""
    triage_service = PTaaSTriageService(db)
    report = triage_service.get_executive_report(report_id)
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Check access
    ptaas_service = PTaaSService(db)
    engagement = ptaas_service.get_engagement(report.engagement_id)
    
    org_id = current_user.organization.id if current_user.organization else None
    if engagement.organization_id != org_id:
        if not is_ptaas_admin_or_staff(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    return report


@router.get("/engagements/{engagement_id}/executive-reports", response_model=List[PTaaSExecutiveReportResponse])
def get_engagement_reports(
    engagement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all executive reports for engagement - FREQ-36"""
    ptaas_service = PTaaSService(db)
    engagement = ptaas_service.get_engagement(engagement_id)
    
    if not engagement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Engagement not found"
        )
    
    # Check access
    org_id = current_user.organization.id if current_user.organization else None
    if engagement.organization_id != org_id:
        if not is_ptaas_admin_or_staff(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    triage_service = PTaaSTriageService(db)
    return triage_service.get_engagement_reports(engagement_id)


@router.post("/executive-reports/{report_id}/approve", response_model=PTaaSExecutiveReportResponse)
def approve_executive_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Approve executive report - FREQ-36
    Organization members or staff can approve
    """
    triage_service = PTaaSTriageService(db)
    report = triage_service.get_executive_report(report_id)
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Check access
    ptaas_service = PTaaSService(db)
    engagement = ptaas_service.get_engagement(report.engagement_id)
    
    org_id = current_user.organization.id if current_user.organization else None
    if engagement.organization_id != org_id:
        if not is_ptaas_admin_or_staff(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    return triage_service.approve_report(report_id, current_user.id)


# Retest Endpoints - FREQ-37
from src.services.ptaas_retest_service import PTaaSRetestService
from src.api.v1.schemas.ptaas_retest import (
    PTaaSRetestPolicyCreate,
    PTaaSRetestPolicyResponse,
    PTaaSRetestRequestCreate,
    PTaaSRetestRequestResponse,
    PTaaSRetestAssignment,
    PTaaSRetestCompletion,
    PTaaSRetestEligibilityResponse,
    PTaaSRetestStatisticsResponse
)


@router.post("/engagements/{engagement_id}/retest-policy", response_model=PTaaSRetestPolicyResponse, status_code=status.HTTP_201_CREATED)
def create_retest_policy(
    engagement_id: UUID,
    policy_data: PTaaSRetestPolicyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create or update retest policy for engagement - FREQ-37
    Defines rules for free retesting period
    """
    ptaas_service = PTaaSService(db)
    engagement = ptaas_service.get_engagement(engagement_id)
    
    if not engagement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Engagement not found"
        )
    
    # Only org members or staff can set policy
    org_id = current_user.organization.id if current_user.organization else None
    if engagement.organization_id != org_id:
        if not is_ptaas_admin_or_staff(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    retest_service = PTaaSRetestService(db)
    return retest_service.create_retest_policy(engagement_id, policy_data.dict())


@router.get("/engagements/{engagement_id}/retest-policy", response_model=PTaaSRetestPolicyResponse)
def get_retest_policy(
    engagement_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get retest policy for engagement - FREQ-37"""
    retest_service = PTaaSRetestService(db)
    policy = retest_service.get_retest_policy(engagement_id)
    
    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Retest policy not found"
        )
    
    return policy


@router.post("/findings/{finding_id}/retest", response_model=PTaaSRetestRequestResponse, status_code=status.HTTP_201_CREATED)
def request_retest(
    finding_id: UUID,
    retest_data: PTaaSRetestRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Request free retest for fixed vulnerability - FREQ-37
    Organizations can request retesting within eligibility period
    """
    retest_service = PTaaSRetestService(db)
    
    try:
        result = retest_service.request_retest(
            finding_id,
            current_user.id,
            retest_data.dict()
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/findings/{finding_id}/retest-eligibility", response_model=PTaaSRetestEligibilityResponse)
def check_retest_eligibility(
    finding_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Check if finding is eligible for retest - FREQ-37
    Returns eligibility status and remaining retests
    """
    retest_service = PTaaSRetestService(db)
    
    # Get finding to get engagement
    ptaas_service = PTaaSService(db)
    finding = ptaas_service.get_finding(finding_id)
    
    if not finding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Finding not found"
        )
    
    # Get or create policy
    policy = retest_service.get_retest_policy(finding.engagement_id)
    if not policy:
        policy = retest_service.create_retest_policy(
            finding.engagement_id,
            retest_service.get_default_policy()
        )
    
    eligibility = retest_service.check_retest_eligibility(finding_id, policy)
    return eligibility


@router.get("/findings/{finding_id}/retests", response_model=List[PTaaSRetestRequestResponse])
def get_finding_retests(
    finding_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all retest requests for a finding - FREQ-37"""
    retest_service = PTaaSRetestService(db)
    return retest_service.get_finding_retests(finding_id)


@router.get("/engagements/{engagement_id}/retests", response_model=List[PTaaSRetestRequestResponse])
def get_engagement_retests(
    engagement_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all retest requests for engagement - FREQ-37"""
    ptaas_service = PTaaSService(db)
    engagement = ptaas_service.get_engagement(engagement_id)
    
    if not engagement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Engagement not found"
        )
    
    # Check access
    org_id = current_user.organization.id if current_user.organization else None
    if engagement.organization_id != org_id:
        if not is_ptaas_admin_or_staff(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    retest_service = PTaaSRetestService(db)
    return retest_service.get_engagement_retests(engagement_id)


@router.get("/retests/pending", response_model=List[PTaaSRetestRequestResponse])
def get_pending_retests(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get pending retest requests - FREQ-37
    Staff can view all pending retests
    """
    if not is_ptaas_admin_or_staff(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only staff can view pending retests"
        )
    
    retest_service = PTaaSRetestService(db)
    return retest_service.get_pending_retests(limit)


@router.post("/retests/{retest_id}/approve", response_model=PTaaSRetestRequestResponse)
def approve_retest(
    retest_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Approve retest request - FREQ-37
    Staff or org members can approve
    """
    retest_service = PTaaSRetestService(db)
    retest = retest_service.get_retest_request(retest_id)
    
    if not retest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Retest request not found"
        )
    
    # Check access
    ptaas_service = PTaaSService(db)
    engagement = ptaas_service.get_engagement(retest.engagement_id)
    
    org_id = current_user.organization.id if current_user.organization else None
    if engagement.organization_id != org_id:
        if not is_ptaas_admin_or_staff(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    return retest_service.approve_retest(retest_id, current_user.id)


@router.post("/retests/{retest_id}/assign", response_model=PTaaSRetestRequestResponse)
def assign_retest(
    retest_id: UUID,
    assignment: PTaaSRetestAssignment,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Assign retest to researcher - FREQ-37
    Staff or org members can assign
    """
    if not is_ptaas_admin_or_staff(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only staff can assign retests"
        )
    
    retest_service = PTaaSRetestService(db)
    return retest_service.assign_retest(
        retest_id,
        assignment.assigned_to,
        current_user.id
    )


@router.post("/retests/{retest_id}/complete", response_model=PTaaSRetestRequestResponse)
def complete_retest(
    retest_id: UUID,
    completion: PTaaSRetestCompletion,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Complete retest with results - FREQ-37
    Assigned researcher or staff can complete
    """
    try:
        retest_service = PTaaSRetestService(db)
        retest = retest_service.get_retest_request(retest_id)
        
        if not retest:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Retest request not found"
            )
        
        # Check if user has permission to complete retest
        # Allow if: assigned to user, user is staff, or user is assigned to the engagement
        ptaas_service = PTaaSService(db)
        engagement = ptaas_service.get_engagement(retest.engagement_id)
        
        is_assigned_to_retest = retest.assigned_to == current_user.id if retest.assigned_to else False
        is_assigned_to_engagement = str(current_user.id) in (engagement.assigned_researchers or []) if engagement else False
        is_staff = is_ptaas_admin_or_staff(current_user)
        
        # Debug logging
        print(f"🔍 RETEST AUTHORIZATION CHECK")
        print(f"Current User ID: {current_user.id} (type: {type(current_user.id)})")
        print(f"Current User Role: {current_user.role}")
        print(f"Retest Assigned To: {retest.assigned_to}")
        print(f"Engagement Assigned Researchers: {engagement.assigned_researchers if engagement else None}")
        print(f"Is Assigned to Retest: {is_assigned_to_retest}")
        print(f"Is Assigned to Engagement: {is_assigned_to_engagement}")
        print(f"Is Staff: {is_staff}")
        
        if not (is_assigned_to_retest or is_assigned_to_engagement or is_staff):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only assigned researcher or staff can complete retest"
            )
        
        # Convert completion data to dict, handling Enum properly
        completion_data = completion.model_dump()
        if isinstance(completion_data.get('retest_result'), str):
            # Already a string, no conversion needed
            pass
        
        return retest_service.complete_retest(
            retest_id,
            current_user.id,
            completion_data
        )
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"ERROR in complete_retest: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error: {str(e)}"
        )


@router.get("/engagements/{engagement_id}/retest-statistics", response_model=PTaaSRetestStatisticsResponse)
def get_retest_statistics(
    engagement_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get retest statistics for engagement - FREQ-37"""
    ptaas_service = PTaaSService(db)
    engagement = ptaas_service.get_engagement(engagement_id)
    
    if not engagement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Engagement not found"
        )
    
    # Check access
    org_id = current_user.organization.id if current_user.organization else None
    if engagement.organization_id != org_id:
        if not is_ptaas_admin_or_staff(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    retest_service = PTaaSRetestService(db)
    return retest_service.get_retest_statistics(engagement_id)


# Finding Assignment - Step 8
from pydantic import BaseModel as PydanticBaseModel

class FindingAssignmentRequest(PydanticBaseModel):
    assigned_to: UUID
    notes: Optional[str] = None


@router.post("/findings/{finding_id}/assign")
def assign_finding_to_team(
    finding_id: UUID,
    assignment: FindingAssignmentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Assign finding to team member - Step 8"""
    service = PTaaSService(db)
    
    finding = service.get_finding(finding_id)
    if not finding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Finding not found"
        )
    
    # Update finding with assignment
    update_data = {
        'assigned_to': assignment.assigned_to,
    }
    
    updated_finding = service.update_finding(finding_id, update_data, current_user.id)
    return updated_finding


# Comments & Communication - Step 9
from src.services.ptaas_comments_service import PTaaSCommentsService

class CommentCreateRequest(PydanticBaseModel):
    content: str
    attachments: Optional[List[str]] = None


class CommentUpdateRequest(PydanticBaseModel):
    content: str


@router.post("/findings/{finding_id}/comments")
def add_finding_comment(
    finding_id: UUID,
    comment: CommentCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add comment to finding - Step 9"""
    comments_service = PTaaSCommentsService(db)
    
    try:
        new_comment = comments_service.add_comment(
            finding_id=finding_id,
            user_id=current_user.id,
            content=comment.content,
            attachments=comment.attachments
        )
        return new_comment
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/findings/{finding_id}/comments")
def get_finding_comments(
    finding_id: UUID,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all comments for a finding - Step 9"""
    comments_service = PTaaSCommentsService(db)
    comments = comments_service.get_comments(finding_id, limit)
    return comments


@router.patch("/comments/{comment_id}")
def update_comment(
    comment_id: UUID,
    comment_update: CommentUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update comment - Step 9"""
    comments_service = PTaaSCommentsService(db)
    
    try:
        updated_comment = comments_service.update_comment(
            comment_id=comment_id,
            content=comment_update.content,
            user_id=current_user.id
        )
        
        if not updated_comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found"
            )
        
        return updated_comment
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )


@router.delete("/comments/{comment_id}")
def delete_comment(
    comment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete comment - Step 9"""
    comments_service = PTaaSCommentsService(db)
    
    try:
        success = comments_service.delete_comment(comment_id, current_user.id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found"
            )
        
        return {"message": "Comment deleted successfully"}
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )


@router.post("/findings/{finding_id}/attachments")
def add_finding_attachment(
    finding_id: UUID,
    file_url: str,
    file_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add attachment to finding - Step 9"""
    comments_service = PTaaSCommentsService(db)
    
    try:
        attachment = comments_service.add_attachment(
            finding_id=finding_id,
            file_url=file_url,
            file_name=file_name,
            uploaded_by=current_user.id
        )
        return attachment
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/findings/{finding_id}/attachments")
def get_finding_attachments(
    finding_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all attachments for a finding - Step 9"""
    comments_service = PTaaSCommentsService(db)
    attachments = comments_service.get_attachments(finding_id)
    return attachments


# Analytics - Step 11
from src.services.ptaas_analytics_service import PTaaSAnalyticsService


@router.get("/engagements/{engagement_id}/analytics")
def get_engagement_analytics(
    engagement_id: UUID,
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive analytics for engagement - Step 11"""
    ptaas_service = PTaaSService(db)
    engagement = ptaas_service.get_engagement(engagement_id)
    
    if not engagement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Engagement not found"
        )
    
    # Check access
    org_id = current_user.organization.id if current_user.organization else None
    if engagement.organization_id != org_id:
        if not is_ptaas_admin_or_staff(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    analytics_service = PTaaSAnalyticsService(db)
    return analytics_service.get_engagement_analytics(engagement_id)


@router.get("/engagements/{engagement_id}/researcher-performance")
def get_researcher_performance(
    engagement_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get researcher performance metrics - Step 11"""
    ptaas_service = PTaaSService(db)
    engagement = ptaas_service.get_engagement(engagement_id)
    
    if not engagement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Engagement not found"
        )
    
    analytics_service = PTaaSAnalyticsService(db)
    return analytics_service.get_researcher_performance(engagement_id)


# Report Generation - Step 12
from src.services.ptaas_report_service import PTaaSReportService


@router.get("/engagements/{engagement_id}/reports/executive")
def generate_executive_report(
    engagement_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate executive summary report - Step 12"""
    ptaas_service = PTaaSService(db)
    engagement = ptaas_service.get_engagement(engagement_id)
    
    if not engagement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Engagement not found"
        )
    
    # Check access
    org_id = current_user.organization.id if current_user.organization else None
    if engagement.organization_id != org_id:
        if not is_ptaas_admin_or_staff(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    report_service = PTaaSReportService(db)
    return report_service.generate_executive_summary(engagement_id)


@router.get("/engagements/{engagement_id}/reports/technical")
def generate_technical_report(
    engagement_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate detailed technical report - Step 12"""
    ptaas_service = PTaaSService(db)
    engagement = ptaas_service.get_engagement(engagement_id)
    
    if not engagement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Engagement not found"
        )
    
    report_service = PTaaSReportService(db)
    return report_service.generate_technical_report(engagement_id)


@router.get("/engagements/{engagement_id}/reports/compliance")
def generate_compliance_report(
    engagement_id: UUID,
    framework: str = 'PCI_DSS',
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate compliance report - Step 12"""
    ptaas_service = PTaaSService(db)
    engagement = ptaas_service.get_engagement(engagement_id)
    
    if not engagement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Engagement not found"
        )
    
    report_service = PTaaSReportService(db)
    return report_service.generate_compliance_report(engagement_id, framework)


# ============================================
# RESEARCHER ENDPOINTS
# ============================================

@router.get("/researcher/engagements", response_model=List[PTaaSEngagementResponse])
def list_researcher_engagements(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List PTaaS engagements assigned to current researcher
    Researchers see engagements where they are in assigned_researchers array
    """
    if not current_user.researcher:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only researchers can access this endpoint"
        )
    
    service = PTaaSService(db)
    researcher_id = str(current_user.researcher.id)  # Use researcher.id, not user.id
    
    # Get all engagements where researcher is assigned
    from src.domain.models.ptaas import PTaaSEngagement
    
    # Get all engagements and filter in Python (most reliable method)
    query = db.query(PTaaSEngagement)
    
    if status:
        query = query.filter(PTaaSEngagement.status == status.upper())
    
    all_engagements = query.order_by(PTaaSEngagement.created_at.desc()).all()
    
    # Filter for researcher in Python
    engagements = [
        eng for eng in all_engagements
        if eng.assigned_researchers and researcher_id in eng.assigned_researchers
    ]
    
    return engagements


@router.get("/researcher/engagements/{engagement_id}", response_model=PTaaSEngagementResponse)
def get_researcher_engagement(
    engagement_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get engagement details for researcher
    Only accessible if researcher is assigned to the engagement
    """
    if not current_user.researcher:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only researchers can access this endpoint"
        )
    
    service = PTaaSService(db)
    engagement = service.get_engagement(engagement_id)
    
    if not engagement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Engagement not found"
        )
    
    # Check if researcher is assigned (use researcher.id, not user.id)
    researcher_id = str(current_user.researcher.id)
    if not engagement.assigned_researchers or researcher_id not in engagement.assigned_researchers:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not assigned to this engagement"
        )
    
    return engagement


@router.post("/researcher/engagements/{engagement_id}/accept")
def accept_engagement(
    engagement_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Researcher accepts engagement assignment
    Updates researcher status to 'accepted'
    """
    if not current_user.researcher:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only researchers can accept engagements"
        )
    
    service = PTaaSService(db)
    engagement = service.get_engagement(engagement_id)
    
    if not engagement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Engagement not found"
        )
    
    # Check if researcher is assigned (use researcher.id, not user.id)
    researcher_id = str(current_user.researcher.id)
    if not engagement.assigned_researchers or researcher_id not in engagement.assigned_researchers:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not assigned to this engagement"
        )
    
    # Log acceptance
    service.audit_service.log_action(
        action_type="ACCEPT_PTAAS_ENGAGEMENT",
        action_category="ptaas",
        target_type="PTaaSEngagement",
        description=f"Researcher accepted PTaaS engagement",
        actor_id=current_user.id,
        target_id=engagement_id,
        metadata={"engagement_name": engagement.name}
    )
    
    # Change status to IN_PROGRESS when researcher accepts
    engagement.status = "IN_PROGRESS"
    db.commit()
    db.refresh(engagement)
    
    return {"message": "Engagement accepted successfully", "engagement_id": str(engagement_id)}
