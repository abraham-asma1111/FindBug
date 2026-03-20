"""Dashboard API Endpoints - FREQ-13."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.api.v1.middlewares.auth import get_current_user
from src.domain.models.user import User
from src.services.dashboard_service import DashboardService


router = APIRouter()


@router.get("/dashboard/researcher", status_code=status.HTTP_200_OK)
def get_researcher_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get researcher dashboard - FREQ-13.
    
    Shows:
    - Submissions overview (total, by status)
    - Earnings summary (total, pending, paid)
    - Rankings and reputation
    - Recent submissions
    - Program participation
    - Monthly trend (6 months)
    
    Only researchers can access.
    """
    if current_user.role != "researcher":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only researchers can access researcher dashboard"
        )
    
    if not current_user.researcher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Researcher profile not found"
        )
    
    service = DashboardService(db)
    
    try:
        dashboard_data = service.get_researcher_dashboard(
            researcher_id=current_user.researcher.id
        )
        return dashboard_data
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/dashboard/organization", status_code=status.HTTP_200_OK)
def get_organization_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get organization dashboard - FREQ-13.
    
    Shows:
    - Program performance (total, active, top programs)
    - Reports overview (total, by status, by severity)
    - Bounty spending (paid, pending, commission)
    - Recent reports
    - Monthly trend (6 months)
    
    Only organizations can access.
    """
    if current_user.role != "organization":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organizations can access organization dashboard"
        )
    
    if not current_user.organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization profile not found"
        )
    
    service = DashboardService(db)
    
    try:
        dashboard_data = service.get_organization_dashboard(
            organization_id=current_user.organization.id
        )
        return dashboard_data
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/dashboard/staff", status_code=status.HTTP_200_OK)
def get_staff_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get staff/triage specialist dashboard - FREQ-13.
    
    Shows:
    - Triage queue (new, triaged, total pending)
    - Priority reports (critical, high, unacknowledged)
    - Status breakdown
    - Recent triage activity
    - Oldest pending reports
    - Daily triage stats (7 days)
    
    Only staff and triage specialists can access.
    """
    if current_user.role not in ["staff", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only staff can access staff dashboard"
        )
    
    service = DashboardService(db)
    
    dashboard_data = service.get_staff_dashboard()
    return dashboard_data


@router.get("/dashboard/admin", status_code=status.HTTP_200_OK)
def get_admin_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get admin platform overview dashboard - FREQ-13.
    
    Shows:
    - User statistics (total, researchers, organizations, active)
    - Program statistics (total, active, new)
    - Report statistics (total, by status, new)
    - Financial overview (paid, pending, platform revenue)
    - Top performers (researchers, organizations)
    - Platform health (pending triage, overdue payouts)
    - Monthly growth trend (6 months)
    
    Only admins can access.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can access admin dashboard"
        )
    
    service = DashboardService(db)
    
    dashboard_data = service.get_admin_dashboard()
    return dashboard_data
