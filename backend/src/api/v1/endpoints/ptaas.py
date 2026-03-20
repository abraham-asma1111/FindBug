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
    PTaaSFindingValidation,
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


@router.post("/findings/{finding_id}/validate", response_model=PTaaSFindingResponse)
def validate_finding(
    finding_id: int,
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
    if current_user.role not in ["ADMIN", "STAFF"]:
        # Check if user is from the engagement's organization
        finding = service.get_finding(finding_id)
        if not finding:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Finding not found"
            )
        
        engagement = service.get_engagement(finding.engagement_id)
        if engagement.organization_id != current_user.organization_id:
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


# Dashboard Endpoints - FREQ-34
from backend.src.services.ptaas_dashboard_service import PTaaSDashboardService
from backend.src.domain.models.ptaas_dashboard import PTaaSTestingPhase
from backend.src.api.v1.schemas.ptaas_dashboard import (
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
    engagement_id: int,
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
    
    # Check access
    if engagement.organization_id != current_user.organization_id:
        if current_user.role not in ["ADMIN", "STAFF"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    dashboard_service = PTaaSDashboardService(db)
    return dashboard_service.get_engagement_dashboard(engagement_id)


@router.post("/engagements/{engagement_id}/initialize-phases", response_model=List[PTaaSTestingPhaseResponse])
def initialize_engagement_phases(
    engagement_id: int,
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
    
    # Check access
    if engagement.organization_id != current_user.organization_id:
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
    phase_id: int,
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
    phase_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get checklist for phase - FREQ-34"""
    dashboard_service = PTaaSDashboardService(db)
    return dashboard_service.get_phase_checklist(phase_id)


@router.post("/checklist/{item_id}/complete", response_model=PTaaSChecklistItemResponse)
def complete_checklist_item(
    item_id: int,
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
    engagement_id: int,
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
    update_id: int,
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
    engagement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get milestones for engagement - FREQ-34"""
    dashboard_service = PTaaSDashboardService(db)
    return dashboard_service.get_engagement_milestones(engagement_id)


@router.post("/milestones/{milestone_id}/complete", response_model=PTaaSMilestoneResponse)
def complete_milestone(
    milestone_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark milestone as complete - FREQ-34"""
    dashboard_service = PTaaSDashboardService(db)
    return dashboard_service.complete_milestone(milestone_id)


# Triage Endpoints - FREQ-36
from backend.src.services.ptaas_triage_service import PTaaSTriageService
from backend.src.api.v1.schemas.ptaas_triage import (
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
    finding_id: int,
    triage_data: PTaaSFindingTriageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Triage and validate a finding - FREQ-36
    Only platform triage specialists (STAFF/ADMIN) can triage
    """
    if current_user.role not in ["ADMIN", "STAFF"]:
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
    finding_id: int,
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
    if current_user.role not in ["ADMIN", "STAFF"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only triage specialists can view pending triage"
        )
    
    triage_service = PTaaSTriageService(db)
    return triage_service.get_pending_triage(limit)


@router.post("/findings/{finding_id}/prioritize", response_model=PTaaSFindingPrioritizationResponse, status_code=status.HTTP_201_CREATED)
def prioritize_finding(
    finding_id: int,
    prioritization: PTaaSFindingPrioritizationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Prioritize a finding - FREQ-36
    Triage specialists can adjust priority with justification
    """
    if current_user.role not in ["ADMIN", "STAFF"]:
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
    engagement_id: int,
    report_data: PTaaSExecutiveReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate compliance-ready executive report - FREQ-36
    Includes risk ratings, evidence summary, and recommendations
    """
    if current_user.role not in ["ADMIN", "STAFF"]:
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
    report_id: int,
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
    
    if engagement.organization_id != current_user.organization_id:
        if current_user.role not in ["ADMIN", "STAFF"]:
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
    if engagement.organization_id != current_user.organization_id:
        if current_user.role not in ["ADMIN", "STAFF"]:
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
    
    if engagement.organization_id != current_user.organization_id:
        if current_user.role not in ["ADMIN", "STAFF"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    return triage_service.approve_report(report_id, current_user.id)


# Retest Endpoints - FREQ-37
from backend.src.services.ptaas_retest_service import PTaaSRetestService
from backend.src.api.v1.schemas.ptaas_retest import (
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
    engagement_id: int,
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
    if engagement.organization_id != current_user.organization_id:
        if current_user.role not in ["ADMIN", "STAFF"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    retest_service = PTaaSRetestService(db)
    return retest_service.create_retest_policy(engagement_id, policy_data.dict())


@router.get("/engagements/{engagement_id}/retest-policy", response_model=PTaaSRetestPolicyResponse)
def get_retest_policy(
    engagement_id: int,
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
    finding_id: int,
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
        return retest_service.request_retest(
            finding_id,
            current_user.id,
            retest_data.dict()
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/findings/{finding_id}/retest-eligibility", response_model=PTaaSRetestEligibilityResponse)
def check_retest_eligibility(
    finding_id: int,
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
    finding_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all retest requests for a finding - FREQ-37"""
    retest_service = PTaaSRetestService(db)
    return retest_service.get_finding_retests(finding_id)


@router.get("/engagements/{engagement_id}/retests", response_model=List[PTaaSRetestRequestResponse])
def get_engagement_retests(
    engagement_id: int,
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
    if engagement.organization_id != current_user.organization_id:
        if current_user.role not in ["ADMIN", "STAFF"]:
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
    if current_user.role not in ["ADMIN", "STAFF"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only staff can view pending retests"
        )
    
    retest_service = PTaaSRetestService(db)
    return retest_service.get_pending_retests(limit)


@router.post("/retests/{retest_id}/approve", response_model=PTaaSRetestRequestResponse)
def approve_retest(
    retest_id: int,
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
    
    if engagement.organization_id != current_user.organization_id:
        if current_user.role not in ["ADMIN", "STAFF"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    return retest_service.approve_retest(retest_id, current_user.id)


@router.post("/retests/{retest_id}/assign", response_model=PTaaSRetestRequestResponse)
def assign_retest(
    retest_id: int,
    assignment: PTaaSRetestAssignment,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Assign retest to researcher - FREQ-37
    Staff or org members can assign
    """
    if current_user.role not in ["ADMIN", "STAFF"]:
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
    retest_id: int,
    completion: PTaaSRetestCompletion,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Complete retest with results - FREQ-37
    Assigned researcher or staff can complete
    """
    retest_service = PTaaSRetestService(db)
    retest = retest_service.get_retest_request(retest_id)
    
    if not retest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Retest request not found"
        )
    
    # Check if user is assigned or staff
    if retest.assigned_to != current_user.id:
        if current_user.role not in ["ADMIN", "STAFF"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only assigned researcher or staff can complete retest"
            )
    
    return retest_service.complete_retest(
        retest_id,
        current_user.id,
        completion.dict()
    )


@router.get("/engagements/{engagement_id}/retest-statistics", response_model=PTaaSRetestStatisticsResponse)
def get_retest_statistics(
    engagement_id: int,
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
    if engagement.organization_id != current_user.organization_id:
        if current_user.role not in ["ADMIN", "STAFF"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    retest_service = PTaaSRetestService(db)
    return retest_service.get_retest_statistics(engagement_id)
