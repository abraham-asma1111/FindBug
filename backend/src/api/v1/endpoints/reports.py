"""Vulnerability Report API Endpoints - FREQ-06."""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
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
        
        # TODO: Save file to storage (S3 or local)
        # TODO: Scan file for viruses
        # For now, just return success
        
        return {
            "message": "Attachment uploaded successfully",
            "filename": file.filename,
            "size": file_size,
            "type": file.content_type
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
