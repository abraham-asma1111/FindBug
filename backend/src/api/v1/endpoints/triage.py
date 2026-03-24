"""Triage Specialist API Endpoints - FREQ-07, FREQ-08."""
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.role_access import (
    can_access_triage_queue,
    can_org_or_triage_staff,
    role_of,
    triage_staff_fk_id,
)
from src.api.v1.middlewares.auth import get_current_user
from src.domain.models.user import User
from src.services.triage_service import TriageService
from src.api.v1.schemas.report import (
    TriageUpdate,
    ReportResponse,
    ReportDetailResponse,
    ReportListResponse,
    ReportStatistics
)


router = APIRouter()


@router.get("/triage/queue", status_code=status.HTTP_200_OK)
def get_triage_queue(
    status_filter: Optional[str] = Query(None, description="Filter by status: new, triaged, valid, invalid, duplicate, resolved"),
    severity_filter: Optional[str] = Query(None, description="Filter by severity: critical, high, medium, low"),
    program_id: Optional[UUID] = Query(None, description="Filter by program"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get triage queue - FREQ-07.
    
    Shows all reports that need triage attention.
    Default: shows 'new' and 'triaged' reports.
    
    Only triage specialists and admins can access.
    """
    if not can_access_triage_queue(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only triage specialists can access the triage queue"
        )
    
    service = TriageService(db)
    
    reports = service.get_triage_queue(
        status=status_filter,
        severity=severity_filter,
        program_id=program_id,
        limit=limit,
        offset=offset
    )
    
    return {
        "reports": reports,
        "total": len(reports),
        "limit": limit,
        "offset": offset
    }


@router.post("/triage/reports/{report_id}/update", status_code=status.HTTP_200_OK)
@router.get("/triage/reports/{report_id}/update", status_code=status.HTTP_200_OK)
def update_report_triage(
    report_id: UUID,
    triage_data: TriageUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update report triage information - FREQ-07, FREQ-08.
    
    Triage specialist can:
    - Update status (new → triaged → valid/invalid/duplicate → resolved)
    - Assign severity (critical, high, medium, low) - FREQ-08
    - Set CVSS score
    - Set VRT category
    - Add triage notes
    - Mark as duplicate
    
    Only triage specialists and admins can update.
    """
    if not can_access_triage_queue(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only triage specialists can update triage information"
        )
    
    service = TriageService(db)
    
    try:
        report = service.update_triage(
            report_id=report_id,
            triage_staff_id=triage_staff_fk_id(current_user),
            actor_user_id=current_user.id,
            actor_role=role_of(current_user).value,
            actor_email=current_user.email,
            status=triage_data.status,
            assigned_severity=triage_data.assigned_severity,
            cvss_score=triage_data.cvss_score,
            vrt_category=triage_data.vrt_category,
            triage_notes=triage_data.triage_notes,
            is_duplicate=triage_data.is_duplicate,
            duplicate_of=triage_data.duplicate_of
        )
        
        return {
            "message": "Report triage updated successfully",
            "report_id": str(report.id),
            "status": report.status,
            "assigned_severity": report.assigned_severity
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update triage: {str(e)}"
        )


@router.post("/triage/reports/{report_id}/mark-duplicate", status_code=status.HTTP_200_OK)
@router.get("/triage/reports/{report_id}/mark-duplicate", status_code=status.HTTP_200_OK)
def mark_as_duplicate(
    report_id: UUID,
    original_report_id: UUID = Query(..., description="ID of the original report"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark report as duplicate - FREQ-07, BR-07.
    
    Links this report to the original report.
    Applies BR-07: Duplicate reports receive 50% bounty if submitted within 24 hours.
    
    Only triage specialists can mark duplicates.
    """
    if not can_access_triage_queue(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only triage specialists can mark duplicates"
        )
    
    service = TriageService(db)
    
    try:
        report = service.mark_as_duplicate(
            report_id=report_id,
            original_report_id=original_report_id,
            triage_staff_id=triage_staff_fk_id(current_user),
            actor_user_id=current_user.id,
        )
        
        return {
            "message": "Report marked as duplicate",
            "report_id": str(report.id),
            "duplicate_of": str(report.duplicate_of),
            "status": report.status
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/triage/reports/{report_id}/similar", status_code=status.HTTP_200_OK)
def find_similar_reports(
    report_id: UUID,
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Find similar reports for duplicate detection - FREQ-07, BR-07.
    
    Helps triage specialists identify potential duplicates.
    Uses title and description similarity.
    
    Only triage specialists can access.
    """
    if not can_access_triage_queue(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only triage specialists can search for similar reports"
        )
    
    service = TriageService(db)
    
    try:
        similar_reports = service.find_similar_reports(
            report_id=report_id,
            limit=limit
        )
        
        return {
            "similar_reports": similar_reports,
            "total": len(similar_reports)
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/triage/reports/{report_id}/acknowledge", status_code=status.HTTP_200_OK)
@router.get("/triage/reports/{report_id}/acknowledge", status_code=status.HTTP_200_OK)
def acknowledge_report(
    report_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Acknowledge report - BR-10.
    
    Organizations must acknowledge reports within 24 hours.
    Sets acknowledged_at timestamp and 90-day remediation deadline.
    
    Only triage specialists and organizations can acknowledge.
    """
    if not can_org_or_triage_staff(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only triage specialists or organizations can acknowledge reports"
        )
    
    service = TriageService(db)
    
    try:
        report = service.acknowledge_report(
            report_id=report_id,
            acknowledged_by=current_user.id
        )
        
        return {
            "message": "Report acknowledged",
            "report_id": str(report.id),
            "acknowledged_at": report.acknowledged_at,
            "remediation_deadline": report.remediation_deadline
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/triage/reports/{report_id}/resolve", status_code=status.HTTP_200_OK)
@router.get("/triage/reports/{report_id}/resolve", status_code=status.HTTP_200_OK)
def resolve_report(
    report_id: UUID,
    resolution_notes: Optional[str] = Query(None, description="Resolution notes"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark report as resolved - FREQ-07.
    
    Indicates the vulnerability has been fixed.
    Sets resolved_at timestamp.
    
    Only triage specialists and organizations can resolve.
    """
    if not can_org_or_triage_staff(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only triage specialists or organizations can resolve reports"
        )
    
    service = TriageService(db)
    
    try:
        report = service.resolve_report(
            report_id=report_id,
            resolved_by=current_user.id,
            resolution_notes=resolution_notes
        )
        
        return {
            "message": "Report resolved",
            "report_id": str(report.id),
            "resolved_at": report.resolved_at,
            "status": report.status
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/triage/statistics", status_code=status.HTTP_200_OK)
def get_triage_statistics(
    program_id: Optional[UUID] = Query(None, description="Filter by program"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get triage statistics - FREQ-15.
    
    Shows report counts by status and severity.
    Helps triage specialists prioritize work.
    
    Only triage specialists and admins can access.
    """
    if not can_access_triage_queue(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only triage specialists can view statistics"
        )
    
    service = TriageService(db)
    
    stats = service.get_statistics(program_id=program_id)
    
    return stats


@router.get("/triage/reports/{report_id}/history", status_code=status.HTTP_200_OK)
def get_report_history(
    report_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get report status history - FREQ-17.
    
    Shows audit trail of all status changes.
    
    Only triage specialists, organizations, and admins can access.
    """
    if not can_org_or_triage_staff(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized access to report history"
        )
    
    service = TriageService(db)
    
    try:
        history = service.get_report_history(report_id=report_id)
        
        return {
            "history": history,
            "total": len(history)
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
