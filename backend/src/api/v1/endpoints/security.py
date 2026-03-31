"""
Security Endpoints — API routes for security logging and audit trail (FREQ-17)
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from src.core.database import get_db
from src.core.security import SecurityAudit
from src.services.security_service import SecurityService
from src.domain.models.user import User
from src.core.dependencies import get_current_user, require_admin
from src.api.v1.schemas.security import (
    SecurityEventsListResponse,
    LoginHistoryListResponse,
    AuditTrailResponse,
    IncidentReportRequest,
    IncidentReportResponse,
    SecurityStatisticsResponse
)

router = APIRouter(prefix="/security", tags=["Security"])


def get_security_service(db: Session = Depends(get_db)) -> SecurityService:
    """Dependency to get SecurityService instance"""
    return SecurityService(db)


@router.get(
    "/events",
    response_model=SecurityEventsListResponse,
    summary="Get Security Events",
    description="Get security events with optional filters (Admin only)"
)
async def get_security_events(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    severity: Optional[str] = Query(None, description="Filter by severity (low, medium, high, critical)"),
    start_date: Optional[str] = Query(None, description="Filter by start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="Filter by end date (ISO format)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(require_admin),
    security_service: SecurityService = Depends(get_security_service)
):
    """
    Get security events with filters (admin only).
    
    Filters:
    - user_id: Filter by specific user
    - event_type: Filter by event type
    - severity: Filter by severity level
    - start_date: Filter by start date
    - end_date: Filter by end date
    """
    try:
        # Parse dates if provided
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None
        
        result = security_service.get_security_events(
            user_id=user_id,
            event_type=event_type,
            severity=severity,
            start_date=start_dt,
            end_date=end_dt,
            skip=skip,
            limit=limit
        )
        
        return SecurityEventsListResponse(**result)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get security events: {str(e)}"
        )


@router.get(
    "/login-history",
    response_model=LoginHistoryListResponse,
    summary="Get Login History",
    description="Get login history with optional filters"
)
async def get_login_history(
    user_id: Optional[str] = Query(None, description="Filter by user ID (admin only)"),
    is_successful: Optional[bool] = Query(None, description="Filter by success status"),
    start_date: Optional[str] = Query(None, description="Filter by start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="Filter by end date (ISO format)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    security_service: SecurityService = Depends(get_security_service)
):
    """
    Get login history.
    
    - Regular users can only see their own login history
    - Admins can see any user's login history
    
    Filters:
    - user_id: Filter by specific user (admin only)
    - is_successful: Filter by success status
    - start_date: Filter by start date
    - end_date: Filter by end date
    """
    try:
        # If user_id is provided and user is not admin, check authorization
        if user_id and user_id != str(current_user.id):
            if current_user.role not in ["admin", "staff"]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only view your own login history."
                )
        
        # If user_id not provided, use current user's ID
        if not user_id:
            user_id = str(current_user.id)
        
        # Parse dates if provided
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None
        
        result = security_service.get_login_history(
            user_id=user_id,
            is_successful=is_successful,
            start_date=start_dt,
            end_date=end_dt,
            skip=skip,
            limit=limit
        )
        
        return LoginHistoryListResponse(**result)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get login history: {str(e)}"
        )


@router.get(
    "/audit-trail",
    response_model=AuditTrailResponse,
    summary="Get Audit Trail",
    description="Get comprehensive audit trail (security events + login history)"
)
async def get_audit_trail(
    user_id: Optional[str] = Query(None, description="User ID (admin only)"),
    days: int = Query(30, ge=1, le=365, description="Number of days to look back"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: User = Depends(get_current_user),
    security_service: SecurityService = Depends(get_security_service)
):
    """
    Get comprehensive audit trail for a user.
    
    - Regular users can only see their own audit trail
    - Admins can see any user's audit trail
    
    Combines:
    - Security events
    - Login history
    
    Sorted by timestamp (most recent first)
    """
    try:
        # If user_id is provided and user is not admin, check authorization
        if user_id and user_id != str(current_user.id):
            if current_user.role not in ["admin", "staff"]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only view your own audit trail."
                )
        
        # If user_id not provided, use current user's ID
        if not user_id:
            user_id = str(current_user.id)
        
        result = security_service.get_audit_trail(
            user_id=user_id,
            days=days,
            skip=skip,
            limit=limit
        )
        
        return AuditTrailResponse(**result)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get audit trail: {str(e)}"
        )


@router.post(
    "/report-incident",
    response_model=IncidentReportResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Report Security Incident",
    description="Report a security incident or suspicious activity"
)
async def report_incident(
    data: IncidentReportRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    security_service: SecurityService = Depends(get_security_service)
):
    """
    Report a security incident.
    
    Users can report:
    - Suspicious activity
    - Unauthorized access attempts
    - Data breaches
    - Phishing attempts
    - Other security concerns
    """
    try:
        result = security_service.report_incident(
            user_id=str(current_user.id),
            incident_type=data.incident_type,
            description=data.description,
            severity=data.severity
        )
        
        # Log security event
        SecurityAudit.log_security_event(
            "INCIDENT_REPORTED",
            str(current_user.id),
            {
                "incident_id": result["incident_id"],
                "incident_type": data.incident_type,
                "severity": data.severity
            },
            request
        )
        
        return IncidentReportResponse(**result)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to report incident: {str(e)}"
        )


@router.get(
    "/statistics",
    response_model=SecurityStatisticsResponse,
    summary="Get Security Statistics",
    description="Get platform security statistics (Admin only)"
)
async def get_security_statistics(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_user: User = Depends(require_admin),
    security_service: SecurityService = Depends(get_security_service)
):
    """
    Get security statistics for the platform (admin only).
    
    Includes:
    - Total security events
    - Events by severity
    - Blocked events
    - Login statistics
    - Success/failure rates
    """
    try:
        result = security_service.get_security_statistics(days=days)
        return SecurityStatisticsResponse(**result)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get security statistics: {str(e)}"
        )
