"""Triage Specialist API Endpoints - FREQ-07, FREQ-08."""
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Query, Body, Request
from sqlalchemy.orm import Session
from sqlalchemy import func, case, Float

from src.core.database import get_db
from src.core.role_access import (
    can_access_triage_queue,
    can_org_or_triage_staff,
    role_of,
    triage_staff_fk_id,
)
from src.api.v1.middlewares.auth import get_current_user
from src.domain.models.user import User
from src.domain.models.report import VulnerabilityReport
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
    
    # Get total count for pagination (without limit/offset)
    query = db.query(VulnerabilityReport)
    
    # Apply same filters as service
    if status_filter:
        query = query.filter(VulnerabilityReport.status == status_filter)
    else:
        # Default: show 'new' and 'triaged' reports
        query = query.filter(VulnerabilityReport.status.in_(['new', 'triaged']))
    
    if severity_filter:
        query = query.filter(
            func.coalesce(VulnerabilityReport.assigned_severity, VulnerabilityReport.suggested_severity) == severity_filter
        )
    
    if program_id:
        query = query.filter(VulnerabilityReport.program_id == program_id)
    
    total_count = query.count()
    
    # Enrich reports with program and researcher names from database
    from src.domain.models.program import BountyProgram
    from src.domain.models.researcher import Researcher
    from src.domain.models.user import User as UserModel
    
    enriched_reports = []
    for report in reports:
        report_dict = {
            "id": str(report.id),
            "report_number": report.report_number,
            "program_id": str(report.program_id) if report.program_id else None,
            "researcher_id": str(report.researcher_id) if report.researcher_id else None,
            "title": report.title,
            "description": report.description,
            "status": report.status,
            "assigned_severity": report.assigned_severity,
            "suggested_severity": report.suggested_severity,
            "triaged_by": str(report.triaged_by) if report.triaged_by else None,
            "triaged_at": report.triaged_at.isoformat() if report.triaged_at else None,
            "is_duplicate": report.is_duplicate,
            "bounty_amount": float(report.bounty_amount) if report.bounty_amount else None,
            "submitted_at": report.submitted_at.isoformat() if report.submitted_at else None,
            "updated_at": report.updated_at.isoformat() if report.updated_at else None,
        }
        
        # Get program name from database
        if report.program_id:
            program = db.query(BountyProgram).filter(BountyProgram.id == report.program_id).first()
            if program:
                report_dict["program_name"] = program.name
        
        # Get researcher name from database
        if report.researcher_id:
            researcher = db.query(Researcher).filter(Researcher.id == report.researcher_id).first()
            if researcher:
                # Construct name, use email as fallback if name is NULL
                full_name = f"{researcher.first_name or ''} {researcher.last_name or ''}".strip()
                
                # Get email from user
                user = db.query(UserModel).filter(UserModel.id == researcher.user_id).first()
                if user:
                    report_dict["researcher_email"] = user.email
                    # Use email username if no name available
                    if not full_name:
                        report_dict["researcher_name"] = user.email.split('@')[0]
                    else:
                        report_dict["researcher_name"] = full_name
        
        enriched_reports.append(report_dict)
    
    return {
        "reports": enriched_reports,
        "total": total_count,
        "limit": limit,
        "offset": offset
    }


@router.post("/triage/reports/{report_id}/update", status_code=status.HTTP_200_OK)
async def update_report_triage(
    report_id: UUID,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update report triage information - FREQ-07, FREQ-08.
    
    Triage specialist can:
    - Update status (new → triaged → valid/invalid/duplicate → resolved)
    - Assign severity (critical, high, medium, low, info) - FREQ-08
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
    
    # Get raw JSON body with detailed logging
    print(f"\n=== TRIAGE UPDATE REQUEST ===")
    print(f"Report ID: {report_id}")
    print(f"User: {current_user.email}")
    
    try:
        body = await request.json()
        print(f"Raw request body: {body}")
        print(f"Body type: {type(body)}")
    except Exception as e:
        print(f"ERROR: Failed to parse JSON: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid JSON: {str(e)}"
        )
    
    # Validate and extract fields
    try:
        print(f"Attempting to validate with TriageUpdate schema...")
        triage_data = TriageUpdate(**body)
        print(f"Validation successful!")
        print(f"Parsed data: {triage_data.dict(exclude_none=True)}")
    except Exception as e:
        # Log the validation error for debugging
        print(f"=== VALIDATION ERROR ===")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print(f"Request body: {body}")
        print(f"Body keys: {list(body.keys()) if isinstance(body, dict) else 'Not a dict'}")
        
        # Try to provide more specific error information
        if hasattr(e, 'errors'):
            print(f"Pydantic errors: {e.errors()}")
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation error: {str(e)}"
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
@router.get("/reports/{report_id}/similar")
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
    
    IMPORTANT: Only returns reports from OTHER researchers.
    - True duplicates = different researchers reporting the same vulnerability
    - Same researcher submitting multiple times = spam/invalid (not duplicates)
    
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
        
        # Format response with researcher information
        formatted_reports = []
        for report in similar_reports:
            report_dict = {
                "id": str(report.id),
                "report_number": report.report_number,
                "title": report.title,
                "status": report.status,
                "submitted_at": report.submitted_at.isoformat() if report.submitted_at else report.created_at.isoformat(),
                "researcher_username": report.researcher.username if report.researcher else "Unknown",
                "researcher_id": str(report.researcher_id) if report.researcher_id else None,
            }
            formatted_reports.append(report_dict)
        
        return {
            "similar_reports": formatted_reports,
            "total": len(formatted_reports)
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
    
    Shows comprehensive report counts by status, severity, and performance metrics.
    Uses DIRECT SQL queries to ensure accurate data from database.
    
    Only triage specialists and admins can access.
    """
    if not can_access_triage_queue(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only triage specialists can view statistics"
        )
    
    # DIRECT SQL QUERIES - NO SERVICE LAYER - 100% REAL DATABASE DATA
    from src.domain.models.researcher import Researcher
    from src.domain.models.user import User as UserModel
    from src.domain.models.program import BountyProgram
    
    # Total reports
    total_reports = db.query(VulnerabilityReport).count()
    
    # Pending triage (status = 'new' or 'triaged')
    pending_triage = db.query(VulnerabilityReport).filter(
        VulnerabilityReport.status.in_(['new', 'triaged'])
    ).count()
    
    # Triaged today
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    triaged_today = db.query(VulnerabilityReport).filter(
        VulnerabilityReport.triaged_at >= today_start
    ).count()
    
    # Average triage time
    avg_triage_time_hours = 0.0
    triaged_reports = db.query(VulnerabilityReport).filter(
        VulnerabilityReport.triaged_at.isnot(None),
        VulnerabilityReport.submitted_at.isnot(None)
    ).all()
    if triaged_reports:
        total_seconds = sum(
            (r.triaged_at - r.submitted_at).total_seconds() 
            for r in triaged_reports
        )
        avg_triage_time_hours = round(total_seconds / len(triaged_reports) / 3600, 2)
    
    # Status breakdown
    status_breakdown = {
        'new': db.query(VulnerabilityReport).filter(VulnerabilityReport.status == 'new').count(),
        'triaged': db.query(VulnerabilityReport).filter(VulnerabilityReport.status == 'triaged').count(),
        'valid': db.query(VulnerabilityReport).filter(VulnerabilityReport.status == 'valid').count(),
        'invalid': db.query(VulnerabilityReport).filter(VulnerabilityReport.status == 'invalid').count(),
        'duplicate': db.query(VulnerabilityReport).filter(VulnerabilityReport.status == 'duplicate').count(),
        'resolved': db.query(VulnerabilityReport).filter(VulnerabilityReport.status == 'resolved').count(),
    }
    
    # Severity breakdown (use assigned_severity if available, otherwise suggested_severity)
    all_reports = db.query(VulnerabilityReport).all()
    severity_breakdown = {
        'critical': sum(1 for r in all_reports if (r.assigned_severity or r.suggested_severity) == 'critical'),
        'high': sum(1 for r in all_reports if (r.assigned_severity or r.suggested_severity) == 'high'),
        'medium': sum(1 for r in all_reports if (r.assigned_severity or r.suggested_severity) == 'medium'),
        'low': sum(1 for r in all_reports if (r.assigned_severity or r.suggested_severity) == 'low'),
        'info': sum(1 for r in all_reports if (r.assigned_severity or r.suggested_severity) == 'info'),
    }
    
    stats = {
        'total_reports': total_reports,
        'pending_triage': pending_triage,
        'triaged_today': triaged_today,
        'avg_triage_time_hours': avg_triage_time_hours,
        'status_breakdown': status_breakdown,
        'severity_breakdown': severity_breakdown,
    }
    
    # Calculate additional metrics for frontend
    
    # Get recent activity (last 6 months for monthly chart)
    six_months_ago = datetime.utcnow() - timedelta(days=180)
    
    recent_activity = db.query(
        func.date(VulnerabilityReport.triaged_at).label('date'),
        func.count(VulnerabilityReport.id).label('triaged_count'),
        func.avg(
            func.extract('epoch', VulnerabilityReport.triaged_at - VulnerabilityReport.submitted_at) / 3600
        ).label('avg_time_hours')
    ).filter(
        VulnerabilityReport.triaged_at >= six_months_ago,
        VulnerabilityReport.triaged_at.isnot(None)
    ).group_by(
        func.date(VulnerabilityReport.triaged_at)
    ).order_by(
        func.date(VulnerabilityReport.triaged_at).desc()
    ).all()
    
    # Get top researchers
    top_researchers = db.query(
        VulnerabilityReport.researcher_id,
        func.count(VulnerabilityReport.id).label('total_reports'),
        func.sum(
            case(
                (VulnerabilityReport.status == 'valid', 1),
                else_=0
            )
        ).label('valid_reports')
    ).filter(
        VulnerabilityReport.researcher_id.isnot(None)
    ).group_by(
        VulnerabilityReport.researcher_id
    ).order_by(
        (func.cast(func.sum(case((VulnerabilityReport.status == 'valid', 1), else_=0)), Float) / 
         func.cast(func.count(VulnerabilityReport.id), Float)).desc()
    ).limit(5).all()
    
    # Get researcher emails
    from src.domain.models.user import User as UserModel
    from src.domain.models.researcher import Researcher
    researcher_stats = []
    for r in top_researchers:
        # Get researcher to find user_id
        researcher = db.query(Researcher).filter(Researcher.id == r.researcher_id).first()
        if researcher:
            user = db.query(UserModel).filter(UserModel.id == researcher.user_id).first()
            email = user.email if user else 'Unknown'
        else:
            email = 'Unknown'
        
        researcher_stats.append({
            'researcher_id': str(r.researcher_id),
            'email': email,
            'total_reports': r.total_reports,
            'valid_reports': r.valid_reports or 0
        })
    
    # Get top programs needing attention
    from src.domain.models.program import BountyProgram
    top_programs = db.query(
        BountyProgram.id,
        BountyProgram.name,
        func.count(VulnerabilityReport.id).label('total_reports'),
        func.sum(
            case(
                (VulnerabilityReport.status.in_(['new', 'triaged']), 1),
                else_=0
            )
        ).label('pending_count')
    ).join(
        VulnerabilityReport,
        VulnerabilityReport.program_id == BountyProgram.id
    ).group_by(
        BountyProgram.id,
        BountyProgram.name
    ).order_by(
        func.sum(
            case(
                (VulnerabilityReport.status.in_(['new', 'triaged']), 1),
                else_=0
            )
        ).desc()
    ).limit(5).all()
    
    program_stats = [{
        'program_id': str(p.id),
        'name': p.name,
        'total_reports': p.total_reports,
        'pending_count': p.pending_count or 0
    } for p in top_programs]
    
    # Calculate triage performance
    this_week_start = datetime.utcnow() - timedelta(days=7)
    last_week_start = datetime.utcnow() - timedelta(days=14)
    
    total_triaged_this_week = db.query(VulnerabilityReport).filter(
        VulnerabilityReport.triaged_at >= this_week_start
    ).count()
    
    total_triaged_last_week = db.query(VulnerabilityReport).filter(
        VulnerabilityReport.triaged_at >= last_week_start,
        VulnerabilityReport.triaged_at < this_week_start
    ).count()
    
    # Calculate accuracy rate (valid reports / total triaged)
    total_triaged = db.query(VulnerabilityReport).filter(
        VulnerabilityReport.status.in_(['valid', 'invalid', 'duplicate'])
    ).count()
    
    valid_count = db.query(VulnerabilityReport).filter(
        VulnerabilityReport.status == 'valid'
    ).count()
    
    accuracy_rate = (valid_count / total_triaged * 100) if total_triaged > 0 else 0
    
    # Calculate average response time
    avg_response = db.query(
        func.avg(
            func.extract('epoch', VulnerabilityReport.triaged_at - VulnerabilityReport.submitted_at) / 3600
        )
    ).filter(
        VulnerabilityReport.triaged_at.isnot(None)
    ).scalar() or 0
    
    # Build comprehensive response with REAL DATABASE DATA
    return {
        'total_reports': total_reports,
        'pending_triage': pending_triage,
        'triaged_today': triaged_today,
        'avg_triage_time_hours': avg_triage_time_hours,
        'status_breakdown': status_breakdown,
        'severity_breakdown': severity_breakdown,
        'recent_activity': [
            {
                'date': str(activity.date),
                'triaged_count': activity.triaged_count,
                'avg_time_hours': float(activity.avg_time_hours) if activity.avg_time_hours else 0
            }
            for activity in recent_activity
        ],
        'triage_performance': {
            'total_triaged_this_week': total_triaged_this_week,
            'total_triaged_last_week': total_triaged_last_week,
            'avg_response_time_hours': float(avg_response),
            'accuracy_rate': float(accuracy_rate)
        },
        'top_researchers': researcher_stats,
        'top_programs': program_stats
    }


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


# ============================================
# TRIAGE TEMPLATES ENDPOINTS
# ============================================

@router.get("/triage/templates", status_code=status.HTTP_200_OK)
def get_triage_templates(
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get triage response templates.
    
    Templates help triage specialists respond quickly with standardized messages.
    
    Only triage specialists can access.
    """
    if not can_access_triage_queue(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only triage specialists can access templates"
        )
    
    service = TriageService(db)
    
    try:
        templates = service.get_templates(
            is_active=is_active,
            limit=limit,
            offset=offset
        )
        
        return {
            "templates": templates,
            "total": len(templates),
            "limit": limit,
            "offset": offset
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get templates: {str(e)}"
        )


@router.post("/triage/templates", status_code=status.HTTP_201_CREATED)
async def create_triage_template(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create triage response template.
    
    Categories: validation, rejection, duplicate, need_info, resolved
    
    Only triage specialists can create templates.
    """
    if not can_access_triage_queue(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only triage specialists can create templates"
        )
    
    try:
        body = await request.json()
        print(f"Received body: {body}")
        
        name = body.get('name')
        title = body.get('title')
        content = body.get('content')
        category = body.get('category')
        
        print(f"Parsed: name={name}, title={title}, content={content}, category={category}")
        
        if not all([name, title, content, category]):
            missing = []
            if not name: missing.append('name')
            if not title: missing.append('title')
            if not content: missing.append('content')
            if not category: missing.append('category')
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required fields: {', '.join(missing)}"
            )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error parsing body: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid request body: {str(e)}"
        )
    
    service = TriageService(db)
    
    try:
        print(f"Calling service.create_template with created_by={current_user.id}")
        template = service.create_template(
            name=name,
            title=title,
            content=content,
            category=category,
            created_by=current_user.id
        )
        print(f"Template created successfully: {template}")
        
        return {
            "message": "Template created successfully",
            "template": template
        }
    
    except ValueError as e:
        print(f"ValueError in create_template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        print(f"Exception in create_template: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create template: {str(e)}"
        )


@router.get("/triage/valid-reports-by-severity", status_code=status.HTTP_200_OK)
def get_valid_reports_by_severity(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get valid reports grouped by severity for Finance Dashboard.
    
    Returns count and percentage of valid reports by severity level.
    Used for Finance Dashboard bar chart visualization.
    
    Only finance officers, triage specialists, and admins can access.
    """
    from src.core.dependencies import require_financial
    
    # Check if user has finance or triage access
    user_role = role_of(current_user).value
    if user_role not in ['finance_officer', 'triage_specialist', 'admin', 'super_admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only finance officers, triage specialists, and admins can access this data"
        )
    
    # Query valid reports grouped by severity
    severity_stats = db.query(
        func.coalesce(
            VulnerabilityReport.assigned_severity,
            VulnerabilityReport.suggested_severity
        ).label('severity'),
        func.count(VulnerabilityReport.id).label('count')
    ).filter(
        VulnerabilityReport.status == 'valid'
    ).group_by(
        'severity'
    ).order_by(
        func.count(VulnerabilityReport.id).desc()
    ).all()
    
    total = sum(stat.count for stat in severity_stats)
    
    # Format data for bar chart
    by_severity = []
    for stat in severity_stats:
        severity = stat.severity or 'not_assigned'
        count = stat.count
        percentage = round((count / total * 100) if total > 0 else 0, 1)
        
        by_severity.append({
            'severity': severity,
            'count': count,
            'percentage': percentage
        })
    
    return {
        'total': total,
        'by_severity': by_severity
    }


@router.get("/triage/templates/{template_id}", status_code=status.HTTP_200_OK)
def get_triage_template(
    template_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get triage template by ID.
    
    Only triage specialists can access.
    """
    if not can_access_triage_queue(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only triage specialists can access templates"
        )
    
    service = TriageService(db)
    
    try:
        template = service.get_template(template_id=template_id)
        return template
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.put("/triage/templates/{template_id}", status_code=status.HTTP_200_OK)
async def update_triage_template(
    template_id: UUID,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update triage template.
    
    Only triage specialists can update templates.
    """
    if not can_access_triage_queue(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only triage specialists can update templates"
        )
    
    try:
        body = await request.json()
        name = body.get('name')
        title = body.get('title')
        content = body.get('content')
        category = body.get('category')
        is_active = body.get('is_active')
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid request body: {str(e)}"
        )
    
    service = TriageService(db)
    
    try:
        template = service.update_template(
            template_id=template_id,
            name=name,
            title=title,
            content=content,
            category=category,
            is_active=is_active
        )
        
        return {
            "message": "Template updated successfully",
            "template": template
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/triage/templates/{template_id}", status_code=status.HTTP_200_OK)
def delete_triage_template(
    template_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete triage template.
    
    Only triage specialists can delete templates.
    """
    if not can_access_triage_queue(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only triage specialists can delete templates"
        )
    
    service = TriageService(db)
    
    try:
        service.delete_template(template_id=template_id)
        
        return {
            "message": "Template deleted successfully",
            "template_id": str(template_id)
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# ============================================
# TRIAGE RESEARCHERS ENDPOINTS
# ============================================

@router.get("/triage/researchers/{researcher_id}", status_code=status.HTTP_200_OK)
def get_triage_researcher_detail(
    researcher_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get researcher triage details.
    
    Shows detailed triage metrics for a specific researcher.
    
    Only triage specialists can access.
    """
    if not can_access_triage_queue(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only triage specialists can access researcher details"
        )
    
    service = TriageService(db)
    
    try:
        researcher = service.get_researcher_detail(researcher_id=researcher_id)
        return researcher
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# ============================================
# TRIAGE PROGRAMS ENDPOINTS
# ============================================

@router.get("/triage/programs", status_code=status.HTTP_200_OK)
def get_triage_programs(
    search: Optional[str] = Query(None, description="Search by program name"),
    sort_by: str = Query("pending_count", description="Sort by: pending_count, total_reports, avg_triage_time"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get programs with triage metrics.
    
    Shows program statistics from triage perspective:
    - Pending reports count
    - Total reports count
    - Average triage time
    - Valid/Invalid ratio
    
    Only triage specialists can access.
    """
    if not can_access_triage_queue(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only triage specialists can access program metrics"
        )
    
    service = TriageService(db)
    
    try:
        programs = service.get_programs_with_metrics(
            search=search,
            sort_by=sort_by,
            limit=limit,
            offset=offset
        )
        
        return {
            "programs": programs,
            "total": len(programs),
            "limit": limit,
            "offset": offset
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get programs: {str(e)}"
        )


@router.get("/triage/programs/{program_id}", status_code=status.HTTP_200_OK)
def get_triage_program_detail(
    program_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get program triage details.
    
    Shows detailed triage metrics for a specific program.
    
    Only triage specialists can access.
    """
    if not can_access_triage_queue(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only triage specialists can access program details"
        )
    
    service = TriageService(db)
    
    try:
        program = service.get_program_detail(program_id=program_id)
        return program
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )



@router.get("/triage/researchers", status_code=status.HTTP_200_OK)
def get_researchers_list(
    search: Optional[str] = Query(None, description="Search by username or email"),
    sort_by: Optional[str] = Query("total_reports", description="Sort by: total_reports, duplicates, spam_score"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get list of researchers with their report statistics.
    
    Shows:
    - Total reports submitted
    - Valid reports count
    - Duplicate reports count
    - Invalid/spam reports count
    - Spam score (percentage of duplicates/invalid)
    
    Only triage specialists can access.
    """
    if not can_access_triage_queue(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only triage specialists can access researcher list"
        )
    
    from src.domain.models.researcher import Researcher
    from src.domain.models.user import User as UserModel
    
    # Build query to get researchers with report counts
    query = db.query(
        Researcher.id,
        Researcher.username,
        Researcher.reputation_score,
        UserModel.email,
        func.count(VulnerabilityReport.id).label('total_reports'),
        func.sum(case((VulnerabilityReport.status == 'valid', 1), else_=0)).label('valid_reports'),
        func.sum(case((VulnerabilityReport.status == 'duplicate', 1), else_=0)).label('duplicate_reports'),
        # Invalid reports: ALL reports with status='invalid' (including those that are also duplicates)
        func.sum(case((VulnerabilityReport.status == 'invalid', 1), else_=0)).label('invalid_reports')
    ).join(
        UserModel, Researcher.user_id == UserModel.id
    ).outerjoin(
        VulnerabilityReport, Researcher.id == VulnerabilityReport.researcher_id
    ).group_by(
        Researcher.id, Researcher.username, Researcher.reputation_score, UserModel.email
    )
    
    # Apply search filter
    if search:
        query = query.filter(
            (Researcher.username.ilike(f"%{search}%")) |
            (UserModel.email.ilike(f"%{search}%"))
        )
    
    # Get results
    results = query.all()
    
    # Calculate spam score and format response
    researchers = []
    for r in results:
        total = r.total_reports or 0
        valid = r.valid_reports or 0
        duplicates = r.duplicate_reports or 0
        invalid = r.invalid_reports or 0
        # Spam score = only invalid reports (not duplicates)
        # This matches the frontend calculation in researcher detail page
        spam_score = (invalid / total * 100) if total > 0 else 0
        
        print(f"=== RESEARCHER {r.username} ===")
        print(f"Total: {total}, Invalid: {invalid}, Spam Score: {spam_score}")
        
        researchers.append({
            "id": str(r.id),
            "username": r.username or "Unknown",
            "email": r.email,
            "reputation_score": float(r.reputation_score) if r.reputation_score else 0,
            "total_reports": total,
            "valid_reports": valid,
            "duplicate_reports": duplicates,
            "invalid_reports": invalid,
            "spam_score": round(spam_score, 1)
        })
    
    # Sort results
    if sort_by == "duplicates":
        researchers.sort(key=lambda x: x["duplicate_reports"], reverse=True)
    elif sort_by == "spam_score":
        researchers.sort(key=lambda x: x["spam_score"], reverse=True)
    else:  # default: total_reports
        researchers.sort(key=lambda x: x["total_reports"], reverse=True)
    
    # Apply pagination
    paginated = researchers[offset:offset + limit]
    
    return {
        "researchers": paginated,
        "total": len(researchers),
        "limit": limit,
        "offset": offset
    }


@router.get("/triage/researchers/{researcher_id}/reports", status_code=status.HTTP_200_OK)
def get_researcher_reports(
    researcher_id: UUID,
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    show_duplicates_only: bool = Query(False, description="Show only duplicate reports"),
    limit: int = Query(100, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all reports from a specific researcher.
    
    Useful for:
    - Identifying spam patterns
    - Managing duplicate reports from same researcher
    - Reviewing researcher's submission quality
    
    Only triage specialists can access.
    """
    if not can_access_triage_queue(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only triage specialists can access researcher reports"
        )
    
    from src.domain.models.researcher import Researcher
    from src.domain.models.program import BountyProgram
    
    # Verify researcher exists
    researcher = db.query(Researcher).filter(Researcher.id == researcher_id).first()
    if not researcher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Researcher not found"
        )
    
    # Build query
    query = db.query(VulnerabilityReport).filter(
        VulnerabilityReport.researcher_id == researcher_id
    )
    
    # Apply filters
    if status_filter:
        query = query.filter(VulnerabilityReport.status == status_filter)
    
    if show_duplicates_only:
        query = query.filter(VulnerabilityReport.is_duplicate == True)
    
    # Get reports
    reports = query.order_by(VulnerabilityReport.submitted_at.desc()).limit(limit).offset(offset).all()
    
    # Format response
    formatted_reports = []
    for report in reports:
        program = db.query(BountyProgram).filter(BountyProgram.id == report.program_id).first()
        
        formatted_reports.append({
            "id": str(report.id),
            "report_number": report.report_number,
            "title": report.title,
            "status": report.status,
            "assigned_severity": report.assigned_severity,
            "suggested_severity": report.suggested_severity,
            "is_duplicate": report.is_duplicate,
            "duplicate_of": str(report.duplicate_of) if report.duplicate_of else None,
            "bounty_amount": float(report.bounty_amount) if report.bounty_amount else None,
            "submitted_at": report.submitted_at.isoformat() if report.submitted_at else None,
            "program_name": program.name if program else "Unknown",
            "program_id": str(report.program_id) if report.program_id else None
        })
    
    # Get researcher info and calculate stats from ALL reports (not just filtered ones)
    from src.domain.models.user import User as UserModel
    user = db.query(UserModel).filter(UserModel.id == researcher.user_id).first()
    
    # Calculate stats from ALL reports for this researcher
    all_reports_query = db.query(VulnerabilityReport).filter(
        VulnerabilityReport.researcher_id == researcher_id
    )
    all_reports = all_reports_query.all()
    
    total_reports = len(all_reports)
    valid_reports = len([r for r in all_reports if r.status == 'valid'])
    duplicate_reports = len([r for r in all_reports if r.status == 'duplicate'])
    # Invalid reports: ALL reports with status='invalid' (including those that are also duplicates)
    invalid_reports = len([r for r in all_reports if r.status == 'invalid'])
    spam_score = round((invalid_reports / total_reports * 100), 1) if total_reports > 0 else 0
    
    return {
        "researcher": {
            "id": str(researcher.id),
            "username": researcher.username or "Unknown",
            "email": user.email if user else None,
            "reputation_score": researcher.reputation_score or 0
        },
        "reports": formatted_reports,
        "total": len(formatted_reports),
        "stats": {
            "total_reports": total_reports,
            "valid_reports": valid_reports,
            "duplicate_reports": duplicate_reports,
            "invalid_reports": invalid_reports,
            "spam_score": spam_score
        },
        "limit": limit,
        "offset": offset
    }


@router.post("/triage/researchers/{researcher_id}/reports/bulk-action", status_code=status.HTTP_200_OK)
def bulk_action_researcher_reports(
    researcher_id: UUID,
    action: str = Query(..., description="Action: mark_invalid, mark_duplicate"),
    duplicate_of: Optional[UUID] = Query(None, description="Original report ID for duplicates"),
    report_ids: List[UUID] = Body(..., description="List of report IDs to update"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Perform bulk actions on researcher reports.
    
    Actions:
    - mark_invalid: Mark multiple reports as invalid (spam)
    - mark_duplicate: Mark multiple reports as duplicates of an original
    
    Only triage specialists can perform bulk actions.
    """
    print(f"\n=== BULK ACTION REQUEST RECEIVED ===")
    print(f"Researcher ID: {researcher_id}")
    print(f"Action: {action}")
    print(f"Duplicate of: {duplicate_of}")
    print(f"Report IDs: {report_ids}")
    print(f"Report IDs count: {len(report_ids)}")
    print(f"User: {current_user.email}")
    
    if not can_access_triage_queue(current_user):
        print(f"ERROR: User {current_user.email} does not have triage access")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only triage specialists can perform bulk actions"
        )
    
    if action not in ["mark_invalid", "mark_duplicate"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid action. Must be 'mark_invalid' or 'mark_duplicate'"
        )
    
    if action == "mark_duplicate" and not duplicate_of:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="duplicate_of is required for mark_duplicate action"
        )
    
    # Get staff ID for triage tracking
    staff_id = triage_staff_fk_id(current_user)
    
    updated_count = 0
    errors = []
    
    for report_id in report_ids:
        try:
            report = db.query(VulnerabilityReport).filter(
                VulnerabilityReport.id == report_id,
                VulnerabilityReport.researcher_id == researcher_id
            ).first()
            
            if not report:
                errors.append(f"Report {report_id} not found or doesn't belong to researcher")
                continue
            
            if action == "mark_invalid":
                report.status = "invalid"
                report.triage_notes = f"Marked as invalid (spam) via bulk action by triage specialist"
                report.triaged_by = staff_id
                if report.triaged_at is None:
                    report.triaged_at = datetime.utcnow()
            
            elif action == "mark_duplicate":
                report.status = "duplicate"
                report.is_duplicate = True
                report.duplicate_of = duplicate_of
                report.triage_notes = f"Marked as duplicate via bulk action by triage specialist"
                report.triaged_by = staff_id
                if report.triaged_at is None:
                    report.triaged_at = datetime.utcnow()
            
            updated_count += 1
        
        except Exception as e:
            errors.append(f"Error updating report {report_id}: {str(e)}")
    
    db.commit()
    
    return {
        "success": True,
        "updated_count": updated_count,
        "total_requested": len(report_ids),
        "errors": errors if errors else None
    }



@router.get("/triage/researchers/{researcher_id}/duplicate-groups", status_code=status.HTTP_200_OK)
def get_researcher_duplicate_groups(
    researcher_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Group researcher's reports by similarity to identify duplicate submissions.
    
    Uses title similarity to group reports that are likely the same vulnerability
    submitted multiple times by the same researcher.
    
    Returns groups of similar reports with:
    - Group title (most common title)
    - Count of reports in group
    - List of report IDs and details
    - Suggested action (keep first, mark rest as invalid)
    
    Only triage specialists can access.
    """
    if not can_access_triage_queue(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only triage specialists can access duplicate groups"
        )
    
    from src.domain.models.researcher import Researcher
    from difflib import SequenceMatcher
    
    # Verify researcher exists
    researcher = db.query(Researcher).filter(Researcher.id == researcher_id).first()
    if not researcher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Researcher not found"
        )
    
    # Get all reports from researcher
    reports = db.query(VulnerabilityReport).filter(
        VulnerabilityReport.researcher_id == researcher_id
    ).order_by(VulnerabilityReport.submitted_at.asc()).all()
    
    if not reports:
        return {"groups": [], "total_groups": 0}
    
    # Function to calculate title similarity
    def similarity(a: str, b: str) -> float:
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()
    
    # Group reports by similarity (threshold: 0.8 = 80% similar)
    SIMILARITY_THRESHOLD = 0.8
    groups = []
    processed = set()
    
    for i, report in enumerate(reports):
        if report.id in processed:
            continue
        
        # Start a new group
        group = {
            "title": report.title,
            "reports": [{
                "id": str(report.id),
                "report_number": report.report_number,
                "title": report.title,
                "status": report.status,
                "submitted_at": report.submitted_at.isoformat() if report.submitted_at else None,
                "is_duplicate": report.is_duplicate,
                "bounty_amount": float(report.bounty_amount) if report.bounty_amount else None
            }]
        }
        processed.add(report.id)
        
        # Find similar reports
        for j, other_report in enumerate(reports):
            if i != j and other_report.id not in processed:
                if similarity(report.title, other_report.title) >= SIMILARITY_THRESHOLD:
                    group["reports"].append({
                        "id": str(other_report.id),
                        "report_number": other_report.report_number,
                        "title": other_report.title,
                        "status": other_report.status,
                        "submitted_at": other_report.submitted_at.isoformat() if other_report.submitted_at else None,
                        "is_duplicate": other_report.is_duplicate,
                        "bounty_amount": float(other_report.bounty_amount) if other_report.bounty_amount else None
                    })
                    processed.add(other_report.id)
        
        # Only add groups with 2+ reports (actual duplicates)
        if len(group["reports"]) > 1:
            group["count"] = len(group["reports"])
            # Sort by submission date (oldest first)
            group["reports"].sort(key=lambda x: x["submitted_at"] or "")
            group["original_id"] = group["reports"][0]["id"]  # First submitted is original
            group["duplicate_ids"] = [r["id"] for r in group["reports"][1:]]
            groups.append(group)
    
    # Sort groups by count (most duplicates first)
    groups.sort(key=lambda x: x["count"], reverse=True)
    
    return {
        "groups": groups,
        "total_groups": len(groups),
        "total_duplicates": sum(g["count"] - 1 for g in groups)  # -1 because first is original
    }


@router.post("/triage/researchers/{researcher_id}/resolve-duplicate-group", status_code=status.HTTP_200_OK)
@router.post("/researchers/{researcher_id}/resolve-duplicate-group")
def resolve_duplicate_group(
    researcher_id: UUID,
    original_id: UUID = Query(..., description="ID of the original report to keep"),
    duplicate_ids: List[UUID] = Query(..., description="IDs of duplicate reports to mark as invalid"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Resolve a duplicate group by keeping the original and marking duplicates as invalid.
    
    This is the recommended action for same researcher submitting the same report multiple times:
    - Keep the first submission as valid (or triage normally)
    - Mark all subsequent submissions as invalid (spam)
    
    IMPORTANT: This marks reports as status='invalid' WITHOUT setting is_duplicate=True.
    The is_duplicate flag should ONLY be used for different researchers reporting the same vulnerability.
    Same-researcher spam is just invalid, not a true duplicate.
    
    Only triage specialists can perform this action.
    """
    if not can_access_triage_queue(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only triage specialists can resolve duplicate groups"
        )
    
    # Get staff ID for triage tracking
    staff_id = triage_staff_fk_id(current_user)
    
    # Verify original report exists and belongs to researcher
    original = db.query(VulnerabilityReport).filter(
        VulnerabilityReport.id == original_id,
        VulnerabilityReport.researcher_id == researcher_id
    ).first()
    
    if not original:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Original report not found or doesn't belong to researcher"
        )
    
    updated_count = 0
    errors = []
    
    # Mark duplicates as invalid
    for dup_id in duplicate_ids:
        try:
            report = db.query(VulnerabilityReport).filter(
                VulnerabilityReport.id == dup_id,
                VulnerabilityReport.researcher_id == researcher_id
            ).first()
            
            if not report:
                errors.append(f"Report {dup_id} not found or doesn't belong to researcher")
                continue
            
            # Mark as invalid (spam - same report submitted multiple times)
            # NOTE: Do NOT set is_duplicate=True for same-researcher spam
            # is_duplicate should only be True for different researchers reporting the same vulnerability
            report.status = "invalid"
            report.is_duplicate = False  # This is spam, not a true duplicate
            report.duplicate_of = None  # No duplicate relationship for spam
            report.triage_notes = f"Marked as invalid: Same report submitted multiple times by researcher. Original: {original.report_number}"
            report.triaged_by = staff_id
            if report.triaged_at is None:
                report.triaged_at = datetime.utcnow()
            
            updated_count += 1
        
        except Exception as e:
            errors.append(f"Error updating report {dup_id}: {str(e)}")
    
    db.commit()
    
    return {
        "success": True,
        "original_report": {
            "id": str(original.id),
            "report_number": original.report_number,
            "title": original.title
        },
        "updated_count": updated_count,
        "total_requested": len(duplicate_ids),
        "errors": errors if errors else None
    }
