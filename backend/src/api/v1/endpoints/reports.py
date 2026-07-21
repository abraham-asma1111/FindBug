"""Vulnerability Report API Endpoints - FREQ-06."""
from typing import List, Optional, Type
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.logging import get_logger
from src.api.v1.middlewares.auth import get_current_user
from src.domain.models.user import User
from src.services.report_service import ReportService
from src.api.v1.schemas.report import (
    ReportCreate,
    ReportUpdate,
    ReportResponse,
    ReportDetailResponse,
    ReportListResponse,
    CommentCreate,
    CommentResponse
)


router = APIRouter()
logger = get_logger(__name__)


@router.get("/reports", status_code=status.HTTP_200_OK)
def search_reports(
    search: Optional[str] = Query(None, description="Search by title or description"),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    program_id: Optional[UUID] = Query(None, description="Filter by program"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Search and filter reports - FREQ-18, FREQ-19.
    
    Researchers see their own reports.
    Organizations see reports for their programs.
    Triage specialists see all reports.
    """
    service = ReportService(db)
    
    if current_user.is_researcher():
        # Researchers see their own reports
        reports = service.get_researcher_reports(
            researcher_id=current_user.researcher.id,
            status=status_filter,
            limit=limit,
            offset=offset
        )
        
        # Apply search filter if provided
        if search:
            reports = [r for r in reports if search.lower() in r.title.lower() or search.lower() in r.description.lower()]
        
        # Apply severity filter if provided
        if severity:
            reports = [r for r in reports if r.assigned_severity == severity]
        
        return {
            "reports": reports,
            "total": len(reports),
            "limit": limit,
            "offset": offset
        }
    
    elif current_user.is_organization():
        # Organizations see reports for their programs
        if program_id:
            # Filter by specific program
            reports = service.get_program_reports(
                program_id=program_id,
                organization_id=current_user.organization.id,
                status=status_filter,
                limit=limit,
                offset=offset
            )
        else:
            # Get all reports across all organization programs
            reports = service.get_organization_reports(
                organization_id=current_user.organization.id,
                status=status_filter,
                limit=limit,
                offset=offset
            )
        
        # Apply search filter if provided
        if search:
            reports = [r for r in reports if search.lower() in r.title.lower() or (r.description and search.lower() in r.description.lower())]
        
        # Apply severity filter if provided
        if severity:
            reports = [r for r in reports if r.assigned_severity == severity]
        
        # Serialize reports
        serialized_reports = []
        for r in reports:
            # Get program info
            program_data = None
            if r.program_id:
                from src.domain.models.program import BountyProgram
                program = db.query(BountyProgram).filter(BountyProgram.id == r.program_id).first()
                if program:
                    program_data = {
                        "id": str(program.id),
                        "name": program.name
                    }
            
            serialized_reports.append({
                "id": str(r.id),
                "report_number": r.report_number,
                "title": r.title,
                "description": r.description,
                "status": r.status,
                "assigned_severity": r.assigned_severity,
                "suggested_severity": r.suggested_severity,
                "cvss_score": float(r.cvss_score) if r.cvss_score else None,
                "bounty_amount": float(r.bounty_amount) if r.bounty_amount else None,
                "bounty_status": r.bounty_status,
                "submitted_at": r.submitted_at.isoformat() if r.submitted_at else None,
                "program_id": str(r.program_id) if r.program_id else None,
                "program": program_data,
                "researcher_id": str(r.researcher_id) if r.researcher_id else None,
                "is_duplicate": r.is_duplicate
            })
        
        return {
            "reports": serialized_reports,
            "total": len(serialized_reports),
            "limit": limit,
            "offset": offset
        }
    
    else:
        # Triage specialists and admins see all reports
        from src.domain.models.report import VulnerabilityReport
        
        query = db.query(VulnerabilityReport)
        
        if search:
            query = query.filter(
                (VulnerabilityReport.title.ilike(f"%{search}%")) |
                (VulnerabilityReport.description.ilike(f"%{search}%"))
            )
        
        if status_filter:
            query = query.filter(VulnerabilityReport.status == status_filter)
        
        if severity:
            query = query.filter(VulnerabilityReport.assigned_severity == severity)
        
        if program_id:
            query = query.filter(VulnerabilityReport.program_id == program_id)
        
        reports = query.order_by(VulnerabilityReport.submitted_at.desc()).limit(limit).offset(offset).all()
        
        return {
            "reports": [
                {
                    "id": str(r.id),
                    "report_number": r.report_number,
                    "title": r.title,
                    "status": r.status,
                    "assigned_severity": r.assigned_severity,
                    "submitted_at": r.submitted_at,
                    "program_id": str(r.program_id),
                    "researcher_id": str(r.researcher_id) if r.researcher_id else None,
                    "bounty_amount": float(r.bounty_amount) if r.bounty_amount else None,
                    "bounty_status": r.bounty_status,  # Add bounty_status field
                    "is_duplicate": r.is_duplicate,
                    "duplicate_of": str(r.duplicate_of) if r.duplicate_of else None
                }
                for r in reports
            ],
            "total": len(reports),
            "limit": limit,
            "offset": offset
        }


@router.post("/reports", status_code=status.HTTP_201_CREATED)
@router.get("/reports/submit", status_code=status.HTTP_201_CREATED)
def submit_report(
    report_data: ReportCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit a vulnerability report - FREQ-06.
    
    Required fields:
    - title: Vulnerability title (10-500 chars)
    - description: Detailed description (min 50 chars)
    - steps_to_reproduce: Step-by-step reproduction (min 20 chars)
    - impact_assessment: Impact analysis (min 20 chars)
    - suggested_severity: critical, high, medium, or low
    
    Optional fields:
    - affected_asset: Which asset is affected
    - vulnerability_type: Type of vulnerability (XSS, SQLi, etc.)
    
    Only researchers can submit reports.
    Researcher must have joined the program first.
    """
    if not current_user.is_researcher():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only researchers can submit vulnerability reports"
        )
    
    service = ReportService(db)
    
    try:
        report = service.submit_report(
            researcher_id=current_user.researcher.id,
            user_id=current_user.id,  # Pass user_id for status history
            program_id=report_data.program_id,
            title=report_data.title,
            description=report_data.description,
            steps_to_reproduce=report_data.steps_to_reproduce,
            impact_assessment=report_data.impact_assessment,
            suggested_severity=report_data.suggested_severity,
            affected_asset=report_data.affected_asset,
            vulnerability_type=report_data.vulnerability_type
        )
        
        return {
            "message": "Vulnerability report submitted successfully",
            "report_id": str(report.id),
            "report_number": report.report_number,
            "status": report.status
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit report: {str(e)}"
        )



@router.post("/reports/{report_id}/attachments", status_code=status.HTTP_201_CREATED)
def upload_attachment(
    report_id: UUID,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload attachment to a report - FREQ-06, FREQ-21.
    
    Supported file types:
    - Images: png, jpg, jpeg, gif
    - Videos: mp4, avi, mov
    - Documents: pdf, txt
    - Archives: zip (for PoC code)
    
    Max file size: 50MB
    """
    if not current_user.is_researcher():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only researchers can upload attachments"
        )
    
    service = ReportService(db)
    
    try:
        # Verify report belongs to researcher
        report = service.get_report_by_id(
            report_id=report_id,
            user_id=current_user.id,
            user_role=current_user.role
        )
        
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found"
            )
        
        # Validate file type
        allowed_types = [
            'image/png', 'image/jpeg', 'image/jpg', 'image/gif',
            'video/mp4', 'video/avi', 'video/quicktime',
            'application/pdf', 'text/plain',
            'application/zip'
        ]
        
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type {file.content_type} not allowed"
            )
        
        # Validate file size (50MB max)
        max_size = 50 * 1024 * 1024  # 50MB in bytes
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to beginning
        
        if file_size > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File size exceeds 50MB limit"
            )
        
        # Upload attachment
        attachment = service.upload_attachment(
            report_id=report_id,
            file=file,
            user_id=current_user.id
        )
        
        return {
            "message": "Attachment uploaded successfully",
            "attachment_id": str(attachment.id),
            "filename": attachment.filename,
            "original_filename": attachment.original_filename,
            "size": attachment.file_size,
            "type": attachment.file_type,
            "is_safe": attachment.is_safe,
            "uploaded_at": attachment.uploaded_at
        }
    
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload attachment: {str(e)}"
        )


@router.get("/reports/my-reports", status_code=status.HTTP_200_OK)
def get_my_reports(
    status_filter: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all reports submitted by the researcher - FREQ-18.
    
    Filter by status: new, triaged, valid, invalid, duplicate, resolved
    """
    if not current_user.is_researcher():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only researchers can view their reports"
        )
    
    service = ReportService(db)
    
    reports = service.get_researcher_reports(
        researcher_id=current_user.researcher.id,
        status=status_filter,
        limit=limit,
        offset=offset
    )
    
    # Format reports for frontend
    formatted_reports = []
    for report in reports:
        formatted_reports.append({
            "id": str(report.id),
            "title": report.title,
            "severity": report.assigned_severity or report.suggested_severity,
            "status": report.status,
            "program_name": report.program.name if report.program else "Unknown",
            "submitted_at": report.submitted_at.isoformat() if report.submitted_at else None,
            "bounty_amount": float(report.bounty_amount) if report.bounty_amount else None,
            "report_number": report.report_number,
            "vulnerability_type": report.vulnerability_type
        })
    
    return formatted_reports


@router.get("/reports/{report_id}", status_code=status.HTTP_200_OK)
def get_report(
    report_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get report details - FREQ-18.
    
    Researchers can view their own reports.
    Organizations can view reports for their programs.
    Triage specialists can view all reports.
    """
    service = ReportService(db)
    
    try:
        report = service.get_report_by_id(
            report_id=report_id,
            user_id=current_user.id,
            user_role=current_user.role
        )
        
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found"
            )
        
        # Get program info separately to avoid relationship issues
        from src.domain.models.program import BountyProgram
        program = db.query(BountyProgram).filter(BountyProgram.id == report.program_id).first()
        program_data = {
            "id": str(program.id) if program else None,
            "name": program.name if program else "Unknown Program"
        }
        
        # Get researcher info separately
        from src.domain.models.researcher import Researcher
        from src.domain.models.user import User as UserModel
        researcher = db.query(Researcher).filter(Researcher.id == report.researcher_id).first()
        researcher_user = None
        if researcher:
            researcher_user = db.query(UserModel).filter(UserModel.id == researcher.user_id).first()
        
        researcher_username = "Unknown"
        if researcher:
            researcher_username = researcher.username or (researcher_user.email if researcher_user else "Unknown")

        researcher_data = {
            "id": str(researcher.id) if researcher else None,
            "username": researcher_username
        }
        
        # Get attachments separately
        from src.domain.models.report import ReportAttachment
        attachments = db.query(ReportAttachment).filter(ReportAttachment.report_id == report.id).all()
        attachments_data = [
            {
                "id": str(att.id),
                "filename": att.filename,
                "file_type": att.file_type,
                "file_size": att.file_size,
                "uploaded_at": att.uploaded_at.isoformat() if att.uploaded_at else None
            }
            for att in attachments
        ]
        
        return {
            "id": str(report.id),
            "report_number": report.report_number,
            "title": report.title,
            "description": report.description or "",
            "steps_to_reproduce": report.steps_to_reproduce or "",
            "impact_assessment": report.impact_assessment or "",
            "affected_asset": report.affected_asset or "",
            "suggested_severity": report.suggested_severity,
            "vulnerability_type": report.vulnerability_type,
            "status": report.status,
            "assigned_severity": report.assigned_severity,
            "cvss_score": float(report.cvss_score) if report.cvss_score else None,
            "vrt_category": report.vrt_category,
            "bounty_amount": float(report.bounty_amount) if report.bounty_amount else None,
            "bounty_status": report.bounty_status,  # Add bounty_status field
            "is_duplicate": report.is_duplicate,
            "duplicate_of": str(report.duplicate_of) if report.duplicate_of else None,
            "triage_notes": report.triage_notes,
            "triaged_at": report.triaged_at.isoformat() if report.triaged_at else None,
            "triaged_by": str(report.triaged_by) if report.triaged_by else None,
            "submitted_at": report.submitted_at.isoformat() if report.submitted_at else None,
            "created_at": report.submitted_at.isoformat() if report.submitted_at else None,
            "updated_at": report.updated_at.isoformat() if report.updated_at else None,
            "program": program_data,
            "researcher": researcher_data,
            "attachments": attachments_data
        }
    
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        logger.exception("Error getting report %s", report_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving report: {str(e)}"
        )


@router.post("/reports/{report_id}/comments", status_code=status.HTTP_201_CREATED)
@router.get("/reports/{report_id}/comments/add", status_code=status.HTTP_201_CREATED)
def add_comment(
    report_id: UUID,
    comment_data: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add comment to a report - FREQ-09.
    
    Researchers, organizations, and triage specialists can comment.
    """
    service = ReportService(db)
    
    try:
        comment = service.add_comment(
            report_id=report_id,
            user_id=current_user.id,
            user_role=current_user.role,
            comment_text=comment_data.comment_text,
            comment_type=comment_data.comment_type,
            is_internal=comment_data.is_internal
        )
        
        return {
            "message": "Comment added successfully",
            "comment_id": str(comment.id)
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )


@router.get("/reports/{report_id}/comments", status_code=status.HTTP_200_OK)
def get_comments(
    report_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get comments for a report - FREQ-09.
    
    Researchers cannot see internal notes.
    """
    service = ReportService(db)
    
    comments = service.get_comments(
        report_id=report_id,
        user_role=current_user.role
    )
    
    return {
        "comments": comments,
        "total": len(comments)
    }


@router.get("/programs/{program_id}/reports", status_code=status.HTTP_200_OK)
def get_program_reports(
    program_id: UUID,
    status_filter: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all reports for a program - FREQ-19.
    
    Only organization owners can view reports for their programs.
    """
    if not current_user.is_organization():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organizations can view program reports"
        )
    
    service = ReportService(db)
    
    try:
        reports = service.get_program_reports(
            program_id=program_id,
            organization_id=current_user.organization.id,
            status=status_filter,
            limit=limit,
            offset=offset
        )
        
        return {
            "reports": reports,
            "total": len(reports),
            "limit": limit,
            "offset": offset
        }
    
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )



@router.get("/reports/{report_id}/tracking")
@router.post("/reports/{report_id}/tracking")
def get_report_tracking(
    report_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed tracking information for a report - FREQ-18.
    
    Returns timeline, status history, and current state.
    """
    service = ReportService(db)
    
    try:
        # Verify access
        report = service.get_report_by_id(
            report_id=report_id,
            user_id=current_user.id,
            user_role=current_user.role
        )
        
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found"
            )
        
        tracking_info = service.get_report_tracking_info(report_id)
        
        return tracking_info
    
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )


@router.get("/reports/{report_id}/attachments")
@router.post("/reports/{report_id}/attachments")
def get_report_attachments(
    report_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all attachments for a report - FREQ-21.
    """
    service = ReportService(db)
    
    try:
        # Verify access
        report = service.get_report_by_id(
            report_id=report_id,
            user_id=current_user.id,
            user_role=current_user.role
        )
        
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found"
            )
        
        attachments = service.get_attachments(report_id)
        
        return {
            "attachments": [
                {
                    "id": str(att.id),
                    "filename": att.filename,
                    "original_filename": att.original_filename,
                    "file_type": att.file_type,
                    "file_size": att.file_size,
                    "is_safe": att.is_safe,
                    "uploaded_at": att.uploaded_at
                }
                for att in attachments
            ],
            "total": len(attachments)
        }
    
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )


@router.post("/attachments/{attachment_id}/delete")
def delete_attachment(
    attachment_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete an attachment - FREQ-21.
    
    Only report owner or admin can delete attachments.
    """
    service = ReportService(db)
    
    try:
        service.delete_attachment(
            attachment_id=attachment_id,
            user_id=current_user.id,
            user_role=current_user.role
        )
        
        return {"message": "Attachment deleted successfully"}
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )


@router.get("/organization/reports/summary")
@router.post("/organization/reports/summary")
def get_organization_report_summary(
    program_id: Optional[UUID] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get report summary for organization - FREQ-19.
    
    Provides overview of all reports across programs or for a specific program.
    """
    if not current_user.is_organization():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organizations can view report summaries"
        )
    
    service = ReportService(db)
    
    summary = service.get_organization_report_summary(
        organization_id=current_user.organization.id,
        program_id=program_id
    )
    
    return summary



@router.get("/researcher/reports/statistics")
@router.post("/researcher/reports/statistics")
def get_researcher_report_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get researcher's report statistics - FREQ-18.
    
    Provides overview of all submitted reports with status breakdown.
    """
    if not current_user.is_researcher():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only researchers can view their statistics"
        )
    
    service = ReportService(db)
    
    # Get all reports
    all_reports = service.get_researcher_reports(
        researcher_id=current_user.researcher.id,
        limit=1000
    )
    
    # Calculate statistics
    from collections import defaultdict
    
    status_counts = defaultdict(int)
    severity_counts = defaultdict(int)
    total_bounties = 0
    pending_bounties = 0
    
    for report in all_reports:
        status_counts[report.status] += 1
        
        if report.assigned_severity:
            severity_counts[report.assigned_severity] += 1
        
        if report.bounty_amount:
            total_bounties += float(report.bounty_amount)
            if report.bounty_status == "pending":
                pending_bounties += float(report.bounty_amount)
    
    return {
        "total_reports": len(all_reports),
        "status_breakdown": dict(status_counts),
        "severity_breakdown": dict(severity_counts),
        "bounties": {
            "total_earned": total_bounties,
            "pending": pending_bounties,
            "paid": total_bounties - pending_bounties
        },
        "success_rate": round(
            (status_counts.get("valid", 0) / len(all_reports) * 100) if all_reports else 0,
            2
        )
    }


@router.get("/researcher/reports/timeline")
@router.post("/researcher/reports/timeline")
def get_researcher_reports_timeline(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get researcher's report submission timeline - FREQ-18.
    
    Shows report submissions over time.
    """
    if not current_user.is_researcher():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only researchers can view their timeline"
        )
    
    from datetime import timedelta
    from collections import defaultdict
    
    service = ReportService(db)
    
    # Get reports from last N days
    start_date = datetime.utcnow() - timedelta(days=days)
    
    all_reports = service.get_researcher_reports(
        researcher_id=current_user.researcher.id,
        limit=1000
    )
    
    # Filter by date and group by day
    daily_counts = defaultdict(int)
    daily_status = defaultdict(lambda: defaultdict(int))
    
    for report in all_reports:
        if report.submitted_at >= start_date:
            day = report.submitted_at.date().isoformat()
            daily_counts[day] += 1
            daily_status[day][report.status] += 1
    
    # Build timeline
    timeline = []
    current_date = start_date.date()
    end_date = datetime.utcnow().date()
    
    while current_date <= end_date:
        day_str = current_date.isoformat()
        timeline.append({
            "date": day_str,
            "count": daily_counts.get(day_str, 0),
            "status_breakdown": dict(daily_status.get(day_str, {}))
        })
        current_date += timedelta(days=1)
    
    return {
        "timeline": timeline,
        "period_days": days,
        "total_reports": sum(daily_counts.values())
    }


@router.get("/reports/{report_id}/activity")
@router.post("/reports/{report_id}/activity")
def get_report_activity(
    report_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all activity for a report - FREQ-18.
    
    Shows comments, status changes, and other events.
    """
    service = ReportService(db)
    
    try:
        # Verify access
        report = service.get_report_by_id(
            report_id=report_id,
            user_id=current_user.id,
            user_role=current_user.role
        )
        
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found"
            )
        
        # Get tracking info (includes timeline and status history)
        tracking = service.get_report_tracking_info(report_id)
        
        # Get comments
        comments = service.get_comments(
            report_id=report_id,
            user_role=current_user.role
        )
        
        # Combine into activity feed
        activity = []
        
        # Add timeline events
        for event in tracking["timeline"]:
            activity.append({
                "type": "event",
                "event_type": event["event"],
                "timestamp": event["timestamp"],
                "description": event["description"]
            })
        
        # Add comments
        for comment in comments:
            activity.append({
                "type": "comment",
                "timestamp": comment.created_at,
                "author_role": comment.author_role,
                "comment_text": comment.comment_text,
                "is_internal": comment.is_internal
            })
        
        # Sort by timestamp
        activity.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return {
            "report_id": str(report_id),
            "report_number": report.report_number,
            "activity": activity,
            "total_events": len(activity)
        }
    
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )


@router.put("/reports/{report_id}", status_code=status.HTTP_200_OK)
def update_report(
    report_id: UUID,
    report_data: ReportUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a report - Only allowed for reports with status 'new'.
    
    Researchers can only update their own reports.
    """
    if not current_user.is_researcher():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only researchers can update reports"
        )
    
    service = ReportService(db)
    
    # Get the report
    report = service.get_report_by_id(
        report_id=report_id,
        user_id=current_user.id,
        user_role=current_user.role
    )
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Check if report can be edited (only 'new' status)
    if report.status != "new":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only reports with 'new' status can be edited"
        )
    
    # Update fields if provided
    updates = report_data.dict(exclude_unset=True)
    for field_name, value in updates.items():
        setattr(report, field_name, value)
    
    db.commit()
    db.refresh(report)
    
    return {
        "message": "Report updated successfully",
        "report_id": str(report.id),
        "report_number": report.report_number
    }


@router.delete("/reports/{report_id}", status_code=status.HTTP_200_OK)
def delete_report(
    report_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a report - Only allowed for reports with status 'new'.
    
    Researchers can only delete their own reports.
    This is a soft delete (sets deleted_at timestamp).
    """
    if not current_user.is_researcher():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only researchers can delete reports"
        )
    
    service = ReportService(db)
    
    # Get the report
    report = service.get_report_by_id(
        report_id=report_id,
        user_id=current_user.id,
        user_role=current_user.role
    )
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Check if report can be deleted (only 'new' status)
    if report.status != "new":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only reports with 'new' status can be deleted"
        )
    
    # Soft delete
    from datetime import datetime
    report.deleted_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "message": "Report deleted successfully",
        "report_id": str(report.id)
    }


@router.get("/reports/{report_id}/attachments/{attachment_id}/download")
def download_attachment(
    report_id: UUID,
    attachment_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Download an attachment file - FREQ-21.
    
    Returns the file content for download.
    Researchers, organizations, and triage specialists can download attachments.
    """
    from fastapi.responses import FileResponse, StreamingResponse
    from src.domain.models.report import ReportAttachment
    import os
    
    service = ReportService(db)
    
    try:
        # Verify access to report
        report = service.get_report_by_id(
            report_id=report_id,
            user_id=current_user.id,
            user_role=current_user.role
        )
        
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found"
            )
        
        # Get attachment
        attachment = db.query(ReportAttachment).filter(
            ReportAttachment.id == attachment_id,
            ReportAttachment.report_id == report_id
        ).first()
        
        if not attachment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attachment not found"
            )
        
        # Get file path from storage_path
        # Files are stored in data/uploads/ directory
        file_path = f"data/uploads/{attachment.storage_path}"
        
        # Check if file exists
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found on disk"
            )
        
        # Return file
        return FileResponse(
            path=file_path,
            filename=attachment.original_filename or attachment.filename,
            media_type=attachment.file_type
        )
    
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )


@router.post("/reports/{report_id}/approve-bounty", status_code=status.HTTP_200_OK)
def approve_bounty(
    report_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Approve bounty payment for a valid report.
    
    This endpoint:
    1. Validates the report is in 'valid' status
    2. Calculates total cost (bounty + 30% commission)
    3. Checks organization wallet balance
    4. Deducts from organization wallet
    5. Credits platform wallet
    6. Creates bounty_payment record
    7. Notifies Finance Officer
    
    Only organizations can approve bounties for their programs.
    """
    if not current_user.is_organization():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organizations can approve bounties"
        )
    
    from src.services.payment_service import PaymentService
    from src.services.wallet_service import WalletService
    from src.domain.models.report import VulnerabilityReport
    from decimal import Decimal
    import uuid
    
    # Get report
    report = db.query(VulnerabilityReport).filter(
        VulnerabilityReport.id == report_id
    ).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Verify report belongs to organization's program
    if report.program.organization_id != current_user.organization.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only approve bounties for your own programs"
        )
    
    # Verify report is valid
    if report.status != "valid":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Only valid reports can have bounties approved. Current status: {report.status}"
        )
    
    # Verify bounty amount is set
    if not report.bounty_amount or report.bounty_amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bounty amount must be set before approval"
        )
    
    # Check if bounty already approved
    from src.domain.models.bounty_payment import BountyPayment
    existing_payment = db.query(BountyPayment).filter(
        BountyPayment.report_id == report_id,
        BountyPayment.status.in_(["approved", "processing", "completed"])
    ).first()
    
    if existing_payment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bounty has already been approved for this report"
        )
    
    try:
        # Calculate amounts (BR-06: 30% commission)
        bounty_amount = Decimal(str(report.bounty_amount))
        commission = bounty_amount * Decimal("0.30")
        total_cost = bounty_amount + commission
        
        # Initialize services
        wallet_service = WalletService(db)
        payment_service = PaymentService(db)
        
        # Check organization wallet balance
        org_wallet = wallet_service.get_or_create_wallet(
            owner_id=current_user.id,  # Use user_id, not organization_id
            owner_type="organization"
        )
        
        if org_wallet.available_balance < total_cost:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient wallet balance. Required: {float(total_cost)} ETB, Available: {float(org_wallet.available_balance)} ETB"
            )
        
        # Generate saga ID for transaction tracking
        saga_id = f"BOUNTY-{uuid.uuid4().hex[:12].upper()}"
        
        # Step 1: Deduct from organization wallet
        wallet_service.debit_wallet(
            owner_id=current_user.id,  # Use user_id
            owner_type="organization",
            amount=total_cost,
            saga_id=saga_id,
            from_reserved=False,
            reference_type="bounty_approval",
            reference_id=report_id
        )
        
        # Step 2: Credit platform wallet (entire amount goes to platform as queue)
        # Get or create platform wallet (use first admin/finance user)
        from src.domain.models.user import User as UserModel
        platform_user = db.query(UserModel).filter(UserModel.role == "admin").first()
        if not platform_user:
            platform_user = db.query(UserModel).filter(UserModel.role == "finance_officer").first()
        
        if not platform_user:
            # Rollback if no platform user found
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Platform wallet user not found. Please contact support."
            )
        
        wallet_service.credit_wallet(
            owner_id=platform_user.id,
            owner_type="platform",
            amount=total_cost,
            saga_id=saga_id,
            reference_type="bounty_approval",
            reference_id=report_id
        )
        
        # Step 3: Create bounty payment record
        payment = payment_service.create_bounty_payment(
            report_id=report_id,
            bounty_amount=bounty_amount,
            approved_by=current_user.id
        )
        
        # Update payment to approved status
        payment.status = "approved"
        payment.approved_by = current_user.id
        payment.approved_at = datetime.utcnow()
        db.commit()
        db.refresh(payment)
        
        # Step 4: Update report status
        report.bounty_status = "approved"
        db.commit()
        
        # TODO: Step 5: Send notification to Finance Officer
        # This will be implemented when notification service is integrated
        
        logger.info("Bounty approved", extra={
            "report_id": str(report_id),
            "organization_id": str(current_user.organization.id),
            "bounty_amount": float(bounty_amount),
            "commission": float(commission),
            "total_cost": float(total_cost),
            "payment_id": str(payment.payment_id)
        })
        
        return {
            "message": "Bounty approved successfully",
            "payment_id": str(payment.payment_id),
            "transaction_id": payment.transaction_id,
            "bounty_amount": float(bounty_amount),
            "commission": float(commission),
            "total_cost": float(total_cost),
            "status": payment.status
        }
    
    except ValueError as e:
        # Rollback on error
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Rollback on error
        db.rollback()
        logger.error("Failed to approve bounty", extra={
            "report_id": str(report_id),
            "error": str(e)
        })
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to approve bounty: {str(e)}"
        )
