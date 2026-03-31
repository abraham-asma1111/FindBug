"""Vulnerability Report API Endpoints - FREQ-06."""
from typing import List, Optional, Type
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.api.v1.middlewares.auth import get_current_user
from src.domain.models.user import User
from src.services.report_service import ReportService
from src.api.v1.schemas.report import (
    ReportCreate,
    ReportResponse,
    ReportDetailResponse,
    ReportListResponse,
    CommentCreate,
    CommentResponse
)


router = APIRouter()


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
    
    if current_user.role == "researcher":
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
    
    elif current_user.role == "organization":
        # Organizations see reports for their programs
        if not program_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="program_id required for organization users"
            )
        
        reports = service.get_program_reports(
            program_id=program_id,
            organization_id=current_user.organization.id,
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
                    "program_id": str(r.program_id)
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
    if current_user.role != "researcher":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only researchers can submit vulnerability reports"
        )
    
    service = ReportService(db)
    
    try:
        report = service.submit_report(
            researcher_id=current_user.researcher.id,
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
    if current_user.role != "researcher":
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
    if current_user.role != "researcher":
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
    
    return {
        "reports": reports,
        "total": len(reports),
        "limit": limit,
        "offset": offset
    }


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
        
        return report
    
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
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
    if current_user.role != "organization":
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
    if current_user.role != "organization":
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
    if current_user.role != "researcher":
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
    if current_user.role != "researcher":
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
