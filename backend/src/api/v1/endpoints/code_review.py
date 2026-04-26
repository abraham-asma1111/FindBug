"""
Code Review API Endpoints
Implements FREQ-41: Expert Code Review System
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Type
from uuid import UUID

from src.core.database import get_db
from src.api.v1.middlewares.auth import get_current_user
from src.domain.models.user import User
from src.services.code_review_service import CodeReviewService
from src.api.v1.schemas.code_review import (
    CreateEngagementRequest,
    AssignReviewerRequest,
    AddFindingRequest,
    UpdateFindingStatusRequest,
    CodeReviewEngagementResponse,
    CodeReviewFindingResponse,
    EngagementStatsResponse,
    EngagementListResponse,
    FindingListResponse,
    ReviewStatusEnum,
    FindingSeverityEnum,
    FindingStatusEnum
)
from src.domain.models.code_review import ReviewStatus, FindingSeverity, FindingStatus

router = APIRouter(prefix="/code-review", tags=["code-review"])


@router.post("/engagements", response_model=CodeReviewEngagementResponse, status_code=status.HTTP_201_CREATED)
def create_engagement(
    request: CreateEngagementRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new code review engagement
    
    - **title**: Title of the code review
    - **repository_url**: URL to the code repository
    - **review_type**: Type of review (security, performance, etc.)
    """
    if not current_user.is_organization():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organizations can create code review engagements"
        )
    
    service = CodeReviewService(db)
    
    try:
        engagement = service.create_engagement(
            organization_id=current_user.id,
            title=request.title,
            repository_url=request.repository_url,
            review_type=request.review_type.value
        )
        return engagement
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/engagements/{engagement_id}/assign", response_model=CodeReviewEngagementResponse)
def assign_reviewer(
    engagement_id: UUID,
    request: AssignReviewerRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Assign a reviewer to an engagement
    
    - **reviewer_id**: ID of the researcher to assign
    """
    service = CodeReviewService(db)
    
    # Verify engagement exists and user has permission
    engagement = service.get_engagement(engagement_id)
    if not engagement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Engagement not found"
        )
    
    if current_user.is_organization() and engagement.organization_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to assign reviewers to this engagement"
        )
    
    try:
        engagement = service.assign_reviewer(engagement_id, request.reviewer_id)
        return engagement
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/engagements/{engagement_id}/start", response_model=CodeReviewEngagementResponse)
def start_review(
    engagement_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start a code review"""
    service = CodeReviewService(db)
    
    engagement = service.get_engagement(engagement_id)
    if not engagement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Engagement not found"
        )
    
    if current_user.is_researcher() and engagement.reviewer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to start this review"
        )
    
    try:
        engagement = service.start_review(engagement_id)
        return engagement
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/engagements/{engagement_id}/findings", response_model=CodeReviewFindingResponse, status_code=status.HTTP_201_CREATED)
def add_finding(
    engagement_id: UUID,
    request: AddFindingRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a finding to a code review
    
    - **title**: Title of the finding
    - **description**: Detailed description
    - **severity**: Severity level
    - **issue_type**: Type of issue found
    - **file_path**: Path to the file (optional)
    - **line_number**: Line number (optional)
    """
    service = CodeReviewService(db)
    
    engagement = service.get_engagement(engagement_id)
    if not engagement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Engagement not found"
        )
    
    if current_user.is_researcher() and engagement.reviewer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to add findings to this engagement"
        )
    
    try:
        finding = service.add_finding(
            engagement_id=engagement_id,
            title=request.title,
            description=request.description,
            severity=request.severity.value,
            issue_type=request.issue_type.value,
            file_path=request.file_path,
            line_number=request.line_number
        )
        return finding
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch("/findings/{finding_id}/status", response_model=CodeReviewFindingResponse)
def update_finding_status(
    finding_id: UUID,
    request: UpdateFindingStatusRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update finding status"""
    service = CodeReviewService(db)
    
    try:
        finding = service.update_finding_status(finding_id, request.status.value)
        return finding
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/engagements/{engagement_id}/submit", response_model=CodeReviewEngagementResponse)
def submit_report(
    engagement_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit code review report"""
    service = CodeReviewService(db)
    
    engagement = service.get_engagement(engagement_id)
    if not engagement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Engagement not found"
        )
    
    if current_user.is_researcher() and engagement.reviewer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to submit this report"
        )
    
    try:
        engagement = service.submit_report(engagement_id)
        return engagement
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/engagements/{engagement_id}", response_model=CodeReviewEngagementResponse)
def get_engagement(
    engagement_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get engagement details"""
    service = CodeReviewService(db)
    
    engagement = service.get_engagement(engagement_id)
    if not engagement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Engagement not found"
        )
    
    # Check permissions
    if current_user.is_organization() and engagement.organization_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this engagement"
        )
    
    if current_user.is_researcher() and engagement.reviewer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this engagement"
        )
    
    return engagement


@router.get("/engagements", response_model=EngagementListResponse)
def list_engagements(
    engagement_status: Optional[ReviewStatusEnum] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List engagements for current user"""
    service = CodeReviewService(db)
    
    status_value = ReviewStatus(engagement_status.value) if engagement_status else None
    
    if current_user.is_organization():
        engagements = service.get_organization_engagements(current_user.id, status_value)
    elif current_user.is_researcher():
        engagements = service.get_reviewer_engagements(current_user.id, status_value)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to list engagements"
        )
    
    return EngagementListResponse(
        engagements=engagements,
        total=len(engagements)
    )


@router.get("/engagements/{engagement_id}/findings", response_model=FindingListResponse)
def list_findings(
    engagement_id: UUID,
    severity: Optional[FindingSeverityEnum] = None,
    finding_status: Optional[FindingStatusEnum] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List findings for an engagement"""
    service = CodeReviewService(db)
    
    engagement = service.get_engagement(engagement_id)
    if not engagement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Engagement not found"
        )
    
    # Check permissions
    if current_user.is_organization() and engagement.organization_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view findings for this engagement"
        )
    
    if current_user.is_researcher() and engagement.reviewer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view findings for this engagement"
        )
    
    severity_value = FindingSeverity(severity.value) if severity else None
    status_value = FindingStatus(finding_status.value) if finding_status else None
    
    findings = service.get_engagement_findings(engagement_id, severity_value, status_value)
    
    return FindingListResponse(
        findings=findings,
        total=len(findings)
    )


@router.get("/engagements/{engagement_id}/stats", response_model=EngagementStatsResponse)
def get_engagement_stats(
    engagement_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get engagement statistics"""
    service = CodeReviewService(db)
    
    engagement = service.get_engagement(engagement_id)
    if not engagement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Engagement not found"
        )
    
    # Check permissions
    if current_user.is_organization() and engagement.organization_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view stats for this engagement"
        )
    
    if current_user.is_researcher() and engagement.reviewer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view stats for this engagement"
        )
    
    stats = service.get_engagement_stats(engagement_id)
    return stats
