"""Admin endpoints - FREQ-14."""
from typing import Optional
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.authorization import get_current_user, require_role
from src.domain.models.user import User
from src.services.admin_service import AdminService


router = APIRouter(prefix="/admin", tags=["admin"])


# User Management

@router.get("/users")
@router.post("/users")
def get_all_users(
    role: Optional[str] = None,
    status_filter: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    Get all users with filtering - FREQ-14.
    
    Admin only.
    """
    service = AdminService(db)
    
    users = service.get_all_users(
        role=role,
        status=status_filter,
        search=search,
        limit=limit,
        offset=offset
    )
    
    return {
        "users": [
            {
                "id": str(u.id),
                "email": u.email,
                "full_name": u.full_name,
                "role": u.role,
                "is_active": u.is_active,
                "email_verified": u.email_verified,
                "created_at": u.created_at,
                "last_login": u.last_login
            }
            for u in users
        ],
        "total": len(users),
        "limit": limit,
        "offset": offset
    }


@router.get("/users/{user_id}")
@router.post("/users/{user_id}")
def get_user_details(
    user_id: UUID,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    Get detailed user information - FREQ-14.
    
    Admin only.
    """
    service = AdminService(db)
    
    details = service.get_user_details(user_id)
    
    if not details:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return details


@router.post("/users/{user_id}/status")
def update_user_status(
    user_id: UUID,
    is_active: bool,
    reason: Optional[str] = None,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    Activate or deactivate user - FREQ-14.
    
    Admin only.
    """
    service = AdminService(db)
    
    try:
        user = service.update_user_status(
            user_id=user_id,
            is_active=is_active,
            reason=reason
        )
        
        return {
            "message": f"User {'activated' if is_active else 'deactivated'} successfully",
            "user_id": str(user.id),
            "is_active": user.is_active
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/users/{user_id}/role")
def update_user_role(
    user_id: UUID,
    new_role: str,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    Update user role - FREQ-14.
    
    Admin only.
    """
    service = AdminService(db)
    
    try:
        user = service.update_user_role(
            user_id=user_id,
            new_role=new_role
        )
        
        return {
            "message": "User role updated successfully",
            "user_id": str(user.id),
            "role": user.role
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/users/{user_id}/delete")
def delete_user(
    user_id: UUID,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    Soft delete user - FREQ-14.
    
    Admin only.
    """
    service = AdminService(db)
    
    try:
        service.delete_user(user_id)
        
        return {"message": "User deleted successfully"}
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# Program Management

@router.get("/programs")
@router.post("/programs")
def get_all_programs(
    status_filter: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    Get all programs - FREQ-14.
    
    Admin only.
    """
    service = AdminService(db)
    
    programs = service.get_all_programs(
        status=status_filter,
        limit=limit,
        offset=offset
    )
    
    return {
        "programs": [
            {
                "id": str(p.id),
                "name": p.name,
                "status": p.status,
                "organization_id": str(p.organization_id),
                "created_at": p.created_at,
                "total_reports": p.total_reports_received
            }
            for p in programs
        ],
        "total": len(programs),
        "limit": limit,
        "offset": offset
    }


@router.post("/programs/{program_id}/status")
def update_program_status(
    program_id: UUID,
    new_status: str,
    reason: Optional[str] = None,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    Update program status - FREQ-14.
    
    Admin only.
    """
    service = AdminService(db)
    
    try:
        program = service.update_program_status(
            program_id=program_id,
            new_status=new_status,
            reason=reason
        )
        
        return {
            "message": "Program status updated successfully",
            "program_id": str(program.id),
            "status": program.status
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/programs/{program_id}/delete")
def delete_program(
    program_id: UUID,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    Soft delete program - FREQ-14.
    
    Admin only.
    """
    service = AdminService(db)
    
    try:
        service.delete_program(program_id)
        
        return {"message": "Program deleted successfully"}
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# Platform Audits

@router.get("/audit-log")
@router.post("/audit-log")
def get_audit_log(
    action_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 100,
    offset: int = 0,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    Get platform audit log - FREQ-14, FREQ-17.
    
    Admin only.
    """
    service = AdminService(db)
    
    audit_log = service.get_platform_audit_log(
        action_type=action_type,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset
    )
    
    return {
        "audit_log": audit_log,
        "total": len(audit_log),
        "limit": limit,
        "offset": offset
    }


@router.get("/statistics")
@router.post("/statistics")
def get_platform_statistics(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    Get platform-wide statistics - FREQ-14.
    
    Admin only.
    """
    service = AdminService(db)
    
    statistics = service.get_platform_statistics()
    
    return statistics


# Platform Configuration

@router.get("/config")
@router.post("/config")
def get_platform_config(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    Get platform configuration - FREQ-14.
    
    Admin only.
    """
    service = AdminService(db)
    
    config = service.get_platform_config()
    
    return config


@router.post("/config/update")
def update_platform_config(
    config: dict,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    Update platform configuration - FREQ-14.
    
    Admin only.
    """
    service = AdminService(db)
    
    updated_config = service.update_platform_config(config)
    
    return {
        "message": "Platform configuration updated successfully",
        "config": updated_config
    }



# Reports Oversight (FREQ-19 Admin view)

@router.get("/reports")
@router.post("/reports")
def get_all_reports(
    status_filter: Optional[str] = None,
    severity_filter: Optional[str] = None,
    program_id: Optional[UUID] = None,
    organization_id: Optional[UUID] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    Get all reports across platform - FREQ-14, FREQ-19.
    
    Admin can view ALL reports across all organizations.
    """
    service = AdminService(db)
    
    reports = service.get_all_reports(
        status=status_filter,
        severity=severity_filter,
        program_id=program_id,
        organization_id=organization_id,
        limit=limit,
        offset=offset
    )
    
    return {
        "reports": [
            {
                "id": str(r.id),
                "report_number": r.report_number,
                "title": r.title,
                "status": r.status,
                "assigned_severity": r.assigned_severity,
                "program_id": str(r.program_id),
                "researcher_id": str(r.researcher_id),
                "submitted_at": r.submitted_at,
                "bounty_amount": float(r.bounty_amount) if r.bounty_amount else None,
                "bounty_status": r.bounty_status
            }
            for r in reports
        ],
        "total": len(reports),
        "limit": limit,
        "offset": offset
    }


@router.get("/reports/statistics")
@router.post("/reports/statistics")
def get_report_statistics(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    Get platform-wide report statistics - FREQ-14.
    
    Includes duplicate detection, triage stats, etc.
    """
    service = AdminService(db)
    
    statistics = service.get_report_statistics_admin()
    
    return statistics


# Staff Management (FREQ-01, FREQ-14)

@router.get("/staff")
@router.post("/staff")
def get_all_staff(
    department: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    Get all staff members - FREQ-14.
    
    Admin can view all staff across departments.
    """
    service = AdminService(db)
    
    staff = service.get_all_staff(
        department=department,
        limit=limit,
        offset=offset
    )
    
    return {
        "staff": [
            {
                "id": str(s.id),
                "user_id": str(s.user_id),
                "department": s.department,
                "reports_triaged": s.reports_triaged,
                "avg_triage_time_hours": s.avg_triage_time_hours,
                "created_at": s.created_at
            }
            for s in staff
        ],
        "total": len(staff),
        "limit": limit,
        "offset": offset
    }


@router.post("/staff/create")
def create_staff_member(
    email: str,
    full_name: str,
    department: str,
    role: str = "triage_specialist",
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    Create new staff member - FREQ-01, FREQ-14.
    
    Admin can provision new staff accounts.
    """
    service = AdminService(db)
    
    try:
        staff = service.create_staff_member(
            email=email,
            full_name=full_name,
            department=department,
            role=role
        )
        
        return {
            "message": "Staff member created successfully",
            "staff_id": str(staff.id),
            "email": email
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/staff/statistics")
@router.post("/staff/statistics")
def get_staff_statistics(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    Get staff statistics - FREQ-14.
    
    Overview of staff performance and activity.
    """
    service = AdminService(db)
    
    statistics = service.get_staff_statistics()
    
    return statistics


# Researcher Management

@router.get("/researchers")
@router.post("/researchers")
def get_all_researchers(
    search: Optional[str] = None,
    min_reputation: Optional[int] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    Get all researchers - FREQ-14.
    
    Admin can view all researchers with filtering.
    """
    service = AdminService(db)
    
    researchers = service.get_all_researchers(
        search=search,
        min_reputation=min_reputation,
        limit=limit,
        offset=offset
    )
    
    return {
        "researchers": [
            {
                "id": str(r.id),
                "user_id": str(r.user_id),
                "reputation_score": r.reputation_score,
                "total_reports_submitted": r.total_reports_submitted,
                "valid_reports": r.valid_reports,
                "total_earnings": float(r.total_earnings),
                "specializations": r.specializations,
                "created_at": r.created_at
            }
            for r in researchers
        ],
        "total": len(researchers),
        "limit": limit,
        "offset": offset
    }


@router.get("/researchers/statistics")
@router.post("/researchers/statistics")
def get_researcher_statistics(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    Get researcher statistics - FREQ-14.
    
    Platform-wide researcher metrics.
    """
    service = AdminService(db)
    
    statistics = service.get_researcher_statistics()
    
    return statistics


# Organization Management

@router.get("/organizations")
@router.post("/organizations")
def get_all_organizations(
    verified_only: bool = False,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    Get all organizations - FREQ-14.
    
    Admin can view all organizations.
    """
    service = AdminService(db)
    
    organizations = service.get_all_organizations(
        verified_only=verified_only,
        limit=limit,
        offset=offset
    )
    
    return {
        "organizations": [
            {
                "id": str(o.id),
                "user_id": str(o.user_id),
                "company_name": o.company_name,
                "website": o.website,
                "is_verified": o.is_verified,
                "created_at": o.created_at
            }
            for o in organizations
        ],
        "total": len(organizations),
        "limit": limit,
        "offset": offset
    }


@router.post("/organizations/{organization_id}/verify")
def verify_organization(
    organization_id: UUID,
    is_verified: bool,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    Verify or unverify organization - FREQ-14.
    
    Admin can verify organizations.
    """
    service = AdminService(db)
    
    try:
        org = service.verify_organization(
            organization_id=organization_id,
            is_verified=is_verified
        )
        
        return {
            "message": f"Organization {'verified' if is_verified else 'unverified'} successfully",
            "organization_id": str(org.id),
            "is_verified": org.is_verified
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/organizations/statistics")
@router.post("/organizations/statistics")
def get_organization_statistics(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    Get organization statistics - FREQ-14.
    
    Platform-wide organization metrics.
    """
    service = AdminService(db)
    
    statistics = service.get_organization_statistics()
    
    return statistics


# Payment & Commission Tracking (FREQ-20)

@router.get("/payments/overview")
@router.post("/payments/overview")
def get_payment_overview(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    Get payment and commission overview - FREQ-14, FREQ-20.
    
    Track all payments and 30% platform commission.
    """
    service = AdminService(db)
    
    overview = service.get_payment_overview()
    
    return overview


# VRT Management (FREQ-08)

@router.get("/vrt/config")
@router.post("/vrt/config")
def get_vrt_configuration(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    Get VRT taxonomy configuration - FREQ-14, FREQ-08.
    
    Admin can view VRT configuration.
    """
    service = AdminService(db)
    
    config = service.get_vrt_configuration()
    
    return config


@router.post("/vrt/config/update")
def update_vrt_configuration(
    config: dict,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    Update VRT configuration - FREQ-14, FREQ-08.
    
    Admin can update VRT taxonomy and reward tiers.
    """
    service = AdminService(db)
    
    updated_config = service.update_vrt_configuration(config)
    
    return {
        "message": "VRT configuration updated successfully",
        "config": updated_config
    }


# Admin Dashboard Overview

@router.get("/dashboard/overview")
@router.post("/dashboard/overview")
def get_admin_dashboard_overview(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    Get complete admin dashboard overview - FREQ-13, FREQ-14.
    
    Combines all key metrics for admin dashboard.
    """
    service = AdminService(db)
    
    # Get all statistics
    platform_stats = service.get_platform_statistics()
    report_stats = service.get_report_statistics_admin()
    researcher_stats = service.get_researcher_statistics()
    org_stats = service.get_organization_statistics()
    staff_stats = service.get_staff_statistics()
    payment_overview = service.get_payment_overview()
    
    return {
        "platform": platform_stats,
        "reports": report_stats,
        "researchers": researcher_stats,
        "organizations": org_stats,
        "staff": staff_stats,
        "payments": payment_overview,
        "timestamp": datetime.utcnow()
    }
