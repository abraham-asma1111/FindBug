"""Analytics API Endpoints - FREQ-15."""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.api.v1.middlewares.auth import get_current_user
from src.domain.models.user import User
from src.services.analytics_service import AnalyticsService


router = APIRouter()


@router.get("/analytics/vulnerability-trends", status_code=status.HTTP_200_OK)
def get_vulnerability_trends(
    program_id: Optional[UUID] = Query(None, description="Filter by program"),
    organization_id: Optional[UUID] = Query(None, description="Filter by organization"),
    time_period: str = Query('6months', description="Time period: 7days, 30days, 3months, 6months, 1year"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get vulnerability trends analytics - FREQ-15.
    
    Shows:
    - Vulnerability submissions over time
    - Severity distribution trends
    - Status progression trends
    - Top vulnerability types
    - Average time to triage/resolve
    
    Access:
    - Organizations: Can view their own programs
    - Admins/Staff: Can view all
    """
    # Access control
    if current_user.role == "organization":
        if not organization_id:
            if not current_user.organization:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Organization profile not found"
                )
            organization_id = current_user.organization.id
        elif str(organization_id) != str(current_user.organization.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view analytics for your organization"
            )
    elif current_user.role not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organizations, staff, and admins can view vulnerability trends"
        )
    
    service = AnalyticsService(db)
    
    try:
        analytics = service.get_vulnerability_trends(
            program_id=program_id,
            organization_id=organization_id,
            time_period=time_period
        )
        return analytics
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/analytics/program-effectiveness", status_code=status.HTTP_200_OK)
def get_program_effectiveness(
    program_id: Optional[UUID] = Query(None, description="Filter by program"),
    organization_id: Optional[UUID] = Query(None, description="Filter by organization"),
    time_period: str = Query('6months', description="Time period: 7days, 30days, 3months, 6months, 1year"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get program effectiveness analytics - FREQ-15.
    
    Shows:
    - Report volume and quality
    - Response times
    - Resolution rates
    - ROI metrics
    - Researcher engagement
    
    Access:
    - Organizations: Can view their own programs
    - Admins/Staff: Can view all
    """
    # Access control
    if current_user.role == "organization":
        if not organization_id:
            if not current_user.organization:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Organization profile not found"
                )
            organization_id = current_user.organization.id
        elif str(organization_id) != str(current_user.organization.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view analytics for your organization"
            )
    elif current_user.role not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organizations, staff, and admins can view program effectiveness"
        )
    
    service = AnalyticsService(db)
    
    try:
        analytics = service.get_program_effectiveness(
            program_id=program_id,
            organization_id=organization_id,
            time_period=time_period
        )
        return analytics
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/analytics/researcher-performance", status_code=status.HTTP_200_OK)
def get_researcher_performance(
    researcher_id: Optional[UUID] = Query(None, description="Specific researcher (optional)"),
    time_period: str = Query('6months', description="Time period: 7days, 30days, 3months, 6months, 1year"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get researcher performance analytics - FREQ-15.
    
    Shows:
    - Submission trends
    - Success rates
    - Earnings trends
    - Specialization analysis
    - Comparison to peers
    
    Access:
    - Researchers: Can view their own performance
    - Admins/Staff: Can view all researchers
    - Organizations: Can view top researchers (no specific researcher_id)
    """
    # Access control
    if current_user.role == "researcher":
        # Researchers can only view their own performance
        if not current_user.researcher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Researcher profile not found"
            )
        researcher_id = current_user.researcher.id
    elif current_user.role == "organization":
        # Organizations can view top researchers comparison only
        if researcher_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Organizations can only view top researchers comparison"
            )
    elif current_user.role not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized access"
        )
    
    service = AnalyticsService(db)
    
    try:
        analytics = service.get_researcher_performance(
            researcher_id=researcher_id,
            time_period=time_period
        )
        return analytics
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/analytics/my-performance", status_code=status.HTTP_200_OK)
def get_my_performance(
    time_period: str = Query('6months', description="Time period: 7days, 30days, 3months, 6months, 1year"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current researcher's performance analytics - FREQ-15.
    
    Convenience endpoint for researchers to view their own performance.
    
    Only researchers can access.
    """
    if current_user.role != "researcher":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only researchers can access this endpoint"
        )
    
    if not current_user.researcher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Researcher profile not found"
        )
    
    service = AnalyticsService(db)
    
    try:
        analytics = service.get_researcher_performance(
            researcher_id=current_user.researcher.id,
            time_period=time_period
        )
        return analytics
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
