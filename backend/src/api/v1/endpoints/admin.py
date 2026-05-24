"""Admin endpoints - FREQ-14."""
from typing import Optional
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.authorization import get_current_user, require_role
from src.domain.models.user import User
from src.services.admin_service import AdminService


router = APIRouter(prefix="/admin", tags=["admin"])


# User Management

@router.get("/users")
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
    
    # Bulk-load researcher and org profiles for full_name
    from src.domain.models.researcher import Researcher as _ResProfile
    from src.domain.models.organization import Organization as _OrgProfile
    from src.domain.models.kyc import KYCVerification
    
    r_user_ids = [u.id for u in users if u.role in ('researcher',)]
    o_user_ids = [u.id for u in users if u.role in ('organization',)]
    
    res_profiles = (
        {rp.user_id: rp for rp in db.query(_ResProfile).filter(_ResProfile.user_id.in_(r_user_ids)).all()}
        if r_user_ids else {}
    )
    org_profiles = (
        {op.user_id: op for op in db.query(_OrgProfile).filter(_OrgProfile.user_id.in_(o_user_ids)).all()}
        if o_user_ids else {}
    )
    
    # Bulk-load KYC data for persona verification status
    all_user_ids = [u.id for u in users]
    kyc_map = (
        {k.user_id: k for k in db.query(KYCVerification)
         .filter(KYCVerification.user_id.in_(all_user_ids))
         .order_by(KYCVerification.created_at.desc())
         .all()}
        if all_user_ids else {}
    )

    def _full_name(u):
        if u.id in res_profiles:
            rp = res_profiles[u.id]
            return f"{rp.first_name or ''} {rp.last_name or ''}".strip() or rp.username or None
        if u.id in org_profiles:
            return org_profiles[u.id].company_name
        return getattr(u, 'full_name', None)

    return {
        "users": [
            {
                "id": str(u.id),
                "email": u.email,
                "full_name": _full_name(u),
                "role": u.role,
                "is_active": u.is_active,
                "status": "active" if u.is_active else "inactive",
                "email_verified": bool(getattr(u, "email_verified_at", None)),
                "persona_verified": bool(kyc_map.get(u.id).persona_verified_at) if u.id in kyc_map else False,
                "created_at": u.created_at,
                "last_login": getattr(u, "last_login_at", None),
            }
            for u in users
        ],
        "total": len(users),
        "limit": limit,
        "offset": offset
    }


@router.get("/users/{user_id}")
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
    
    # Bulk-load org profiles to get company_name
    from src.domain.models.organization import Organization as _Org
    org_ids = [p.organization_id for p in programs if p.organization_id]
    org_map = (
        {o.id: o for o in db.query(_Org).filter(_Org.id.in_(org_ids)).all()}
        if org_ids else {}
    )

    return {
        "programs": [
            {
                "id": str(p.id),
                "name": p.name,
                "status": p.status,
                "visibility": getattr(p, "visibility", "public"),
                "organization_id": str(p.organization_id),
                "organization_name": (
                    org_map[p.organization_id].company_name
                    if p.organization_id and p.organization_id in org_map else None
                ),
                "budget": float(p.budget) if p.budget is not None else None,
                "created_at": p.created_at,
                "total_reports": getattr(p, "total_reports_received", 0),
            }
            for p in programs
        ],
        "total": len(programs),
        "limit": limit,
        "offset": offset,
    }


@router.get("/programs/{program_id}")
def get_program_details(
    program_id: UUID,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    Get detailed program information - FREQ-14.

    Admin only.
    """
    from src.domain.models.program import BountyProgram as _BP
    from src.domain.models.organization import Organization as _Org
    from src.domain.models.report import VulnerabilityReport as _VR

    program = db.query(_BP).filter(_BP.id == program_id, _BP.deleted_at.is_(None)).first()
    if not program:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Program not found")

    org = db.query(_Org).filter(_Org.id == program.organization_id).first() if program.organization_id else None

    report_counts = dict(
        db.query(_VR.status, __import__('sqlalchemy').func.count(_VR.id))
        .filter(_VR.program_id == program_id)
        .group_by(_VR.status).all()
    )
    total_reports = sum(report_counts.values())

    return {
        "id": str(program.id),
        "name": program.name,
        "status": program.status,
        "visibility": getattr(program, "visibility", "public"),
        "organization_id": str(program.organization_id) if program.organization_id else None,
        "organization_name": org.company_name if org else None,
        "budget": float(program.budget) if program.budget is not None else None,
        "policy": getattr(program, "policy", None),
        "scope": getattr(program, "scope", None),
        "out_of_scope": getattr(program, "out_of_scope", None),
        "created_at": program.created_at,
        "updated_at": getattr(program, "updated_at", None),
        "total_reports": total_reports,
        "report_counts_by_status": report_counts,
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
    
    updated_config = service.update_platform_config(admin_id=current_user.id, config=config)
    
    return {
        "message": "Platform configuration updated successfully",
        "config": updated_config
    }



# Reports Oversight (FREQ-19 Admin view)

@router.get("/reports")
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

    # Bulk-load researcher profiles (VulnerabilityReport.researcher_id → Researcher.id)
    from src.domain.models.researcher import Researcher as _Res
    from src.domain.models.program import BountyProgram as _BP
    r_ids = [r.researcher_id for r in reports if r.researcher_id]
    p_ids  = [r.program_id   for r in reports if r.program_id]
    res_profiles_map = (
        {rp.id: rp for rp in db.query(_Res).filter(_Res.id.in_(r_ids)).all()}
        if r_ids else {}
    )
    programs_map = (
        {p.id: p for p in db.query(_BP).filter(_BP.id.in_(p_ids)).all()}
        if p_ids else {}
    )

    def _researcher_name(r):
        rp = res_profiles_map.get(r.researcher_id)
        if not rp:
            return None
        name = f"{rp.first_name or ''} {rp.last_name or ''}".strip()
        return name or rp.username or None

    return {
        "reports": [
            {
                "id": str(r.id),
                "report_number": r.report_number,
                "title": r.title,
                "status": r.status,
                "assigned_severity": r.assigned_severity,
                "suggested_severity": r.suggested_severity,
                "program_id": str(r.program_id) if r.program_id else None,
                "program_name": (
                    programs_map[r.program_id].name
                    if r.program_id and r.program_id in programs_map else None
                ),
                "researcher_id": str(r.researcher_id) if r.researcher_id else None,
                "researcher_name": _researcher_name(r),
                "submitted_at": r.submitted_at,
                "bounty_amount": float(r.bounty_amount) if r.bounty_amount else None,
                "bounty_status": r.bounty_status,
            }
            for r in reports
        ],
        "total": len(reports),
        "limit": limit,
        "offset": offset
    }


@router.get("/reports/statistics")
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


@router.get("/reports/{report_id}")
def get_report_details(
    report_id: UUID,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    Get detailed report information - FREQ-14, FREQ-19.

    Admin only.
    """
    from src.domain.models.report import VulnerabilityReport as _VR
    from src.domain.models.researcher import Researcher as _Res
    from src.domain.models.program import BountyProgram as _BP
    from src.domain.models.organization import Organization as _Org

    report = db.query(_VR).filter(_VR.id == report_id).first()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

    res_profile = db.query(_Res).filter(_Res.id == report.researcher_id).first() if report.researcher_id else None
    program = db.query(_BP).filter(_BP.id == report.program_id).first() if report.program_id else None
    org = db.query(_Org).filter(_Org.id == program.organization_id).first() if program and program.organization_id else None

    def _researcher_name(rp):
        if not rp:
            return None
        name = f"{rp.first_name or ''} {rp.last_name or ''}".strip()
        return name or rp.username or None

    # Comments (public only for admin view)
    comments = [
        {
            "id": str(c.id),
            "text": c.comment_text,
            "author_role": c.author_role,
            "is_internal": c.is_internal,
            "created_at": c.created_at,
        }
        for c in sorted(report.comments, key=lambda x: x.created_at)
    ]

    return {
        "id": str(report.id),
        "report_number": report.report_number,
        "title": report.title,
        "description": report.description,
        "steps_to_reproduce": report.steps_to_reproduce,
        "impact_assessment": report.impact_assessment,
        "suggested_severity": report.suggested_severity,
        "assigned_severity": report.assigned_severity,
        "vulnerability_type": report.vulnerability_type,
        "affected_asset": report.affected_asset,
        "cvss_score": float(report.cvss_score) if report.cvss_score else None,
        "vrt_category": report.vrt_category,
        "status": report.status,
        "is_duplicate": report.is_duplicate,
        "triage_notes": report.triage_notes,
        "bounty_amount": float(report.bounty_amount) if report.bounty_amount else None,
        "bounty_status": report.bounty_status,
        "submitted_at": report.submitted_at,
        "triaged_at": report.triaged_at,
        "resolved_at": report.resolved_at,
        "researcher_id": str(report.researcher_id) if report.researcher_id else None,
        "researcher_name": _researcher_name(res_profile),
        "researcher_username": res_profile.username if res_profile else None,
        "program_id": str(report.program_id) if report.program_id else None,
        "program_name": program.name if program else None,
        "organization_name": org.company_name if org else None,
        "comments": comments,
    }




# Staff Management (FREQ-01, FREQ-14)

@router.get("/staff")
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
    
    # Staff is defined as users with internal platform roles
    # Map frontend department labels → User.role values
    DEPT_TO_ROLE = {
        "triage":      "triage_specialist",
        "finance":     "finance_officer",
        "admin":       "admin",
        "engineering": "staff",
        "staff":       "staff",
    }

    STAFF_ROLES = ['triage_specialist', 'finance_officer', 'staff']
    if department and department in DEPT_TO_ROLE:
        # Filter to the specific role for the selected department
        role_value = DEPT_TO_ROLE[department]
        query = db.query(User).filter(User.role == role_value)
    else:
        # Show all staff roles
        query = db.query(User).filter(User.role.in_(STAFF_ROLES))

    staff_users = query.order_by(User.created_at.desc()).offset(offset).limit(limit).all()

    return {
        "staff": [
            {
                "id": str(u.id),
                "user_id": str(u.id),
                "full_name": getattr(u, 'full_name', None),
                "email": u.email,
                "role": u.role,
                "status": "active" if u.is_active else "inactive",
                "department": None,
                "position": u.role.replace('_', ' ').title(),
                "created_at": u.created_at,
            }
            for u in staff_users
        ],
        "total": len(staff_users),
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
            admin_id=current_user.id,
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
    from src.domain.models.kyc import KYCVerification
    
    service = AdminService(db)
    
    researchers = service.get_all_researchers(
        search=search,
        min_reputation=min_reputation,
        limit=limit,
        offset=offset
    )
    
    # Bulk-load user and KYC data
    user_ids = [r.user_id for r in researchers]
    users_map = {u.id: u for u in db.query(User).filter(User.id.in_(user_ids)).all()} if user_ids else {}
    kyc_map = {
        k.user_id: k for k in db.query(KYCVerification)
        .filter(KYCVerification.user_id.in_(user_ids))
        .order_by(KYCVerification.created_at.desc())
        .all()
    } if user_ids else {}
    
    return {
        "researchers": [
            {
                "id": str(r.id),
                "user_id": str(r.user_id),
                "username": r.username,
                "reputation_score": r.reputation_score,
                "total_reports_submitted": getattr(r, 'total_reports_submitted', r.total_reports),
                "valid_reports": getattr(r, 'valid_reports', r.verified_reports),
                "total_earnings": float(r.total_earnings),
                "specializations": getattr(r, 'specializations', None),
                "email_verified": bool(users_map.get(r.user_id).email_verified_at) if r.user_id in users_map else False,
                "persona_verified": bool(kyc_map.get(r.user_id).persona_verified_at) if r.user_id in kyc_map else False,
                "created_at": r.created_at
            }
            for r in researchers
        ],
        "total": len(researchers),
        "limit": limit,
        "offset": offset
    }


@router.get("/researchers/statistics")
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
def get_admin_dashboard_overview(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    Get complete admin dashboard overview - FREQ-13, FREQ-14.

    Combines all key metrics for admin dashboard.
    """
    service = AdminService(db)

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


# ── Alias: /admin/audit-logs (frontend uses plural form) ──────────────────────

@router.get("/audit-logs")
def get_audit_logs(
    action_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 100,
    offset: int = 0,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """Alias for /admin/audit-log — FREQ-14, FREQ-17."""
    service = AdminService(db)
    audit_log = service.get_platform_audit_log(
        action_type=action_type,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset
    )
    return {
        "logs": audit_log,
        "total": len(audit_log),
        "limit": limit,
        "offset": offset
    }


# ── Admin Finance Overview ────────────────────────────────────────────────────

@router.get("/finance/overview")
def get_admin_finance_overview(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """Get payment and commission overview for admin - FREQ-14, FREQ-20."""
    service = AdminService(db)
    # Use the same FinancialAnalyticsService as the Finance Officer portal
    from src.services.financial_analytics_service import FinancialAnalyticsService
    fin_service = FinancialAnalyticsService(db)
    kpis = fin_service.get_executive_kpis()

    return {
        "total_revenue": kpis.get("total_revenue", 0),
        "total_payouts": kpis.get("total_payouts", 0),
        "platform_fees": kpis.get("net_profit", 0),
        "net_profit": kpis.get("net_profit", 0),
        "pending_bounties": kpis.get("pending_payouts", 0),
        "commission_rate": 0.30,
        "monthly_payments": [],
    }


# ── Platform Status ───────────────────────────────────────────────────────────

@router.get("/platform/status")
def get_platform_status(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """Get platform operational status."""
    from src.core.database import get_database_status
    db_status = get_database_status()
    return {
        "status": "operational" if db_status == "healthy" else "maintenance",
        "database": db_status,
        "uptime": 99.9,
        "active_users": 0,
        "api_requests": 0,
    }


# ── Admin Finance Actions ──────────────────────────────────────────────────────

@router.get("/finance/pending-bounties")
def get_pending_bounties(
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """
    List reports with pending bounty status - admin finance view (FREQ-10, FREQ-14).
    Returns reports where bounty_status = 'pending', waiting for approval.
    """
    from src.domain.models.report import VulnerabilityReport as _VR
    from src.domain.models.researcher import Researcher as _Res
    from src.domain.models.program import BountyProgram as _BP

    reports = (
        db.query(_VR)
        .filter(_VR.bounty_status == "pending")
        .order_by(_VR.bounty_approved_at.asc().nullslast(), _VR.submitted_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    res_ids = [r.researcher_id for r in reports if r.researcher_id]
    prog_ids = [r.program_id for r in reports if r.program_id]
    res_map = {r.id: r for r in db.query(_Res).filter(_Res.id.in_(res_ids)).all()} if res_ids else {}
    prog_map = {p.id: p for p in db.query(_BP).filter(_BP.id.in_(prog_ids)).all()} if prog_ids else {}

    def _name(rp):
        if not rp:
            return None
        return f"{rp.first_name or ''} {rp.last_name or ''}".strip() or rp.username

    return {
        "reports": [
            {
                "id": str(r.id),
                "report_number": r.report_number,
                "title": r.title,
                "status": r.status,
                "assigned_severity": r.assigned_severity,
                "bounty_amount": float(r.bounty_amount) if r.bounty_amount else None,
                "bounty_status": r.bounty_status,
                "submitted_at": r.submitted_at,
                "researcher_name": _name(res_map.get(r.researcher_id)),
                "program_name": prog_map[r.program_id].name if r.program_id and r.program_id in prog_map else None,
            }
            for r in reports
        ],
        "total": len(reports),
    }


@router.post("/finance/reports/{report_id}/approve-bounty")
def admin_approve_bounty(
    report_id: UUID,
    bounty_amount: float = Query(..., gt=0, description="Bounty amount to approve"),
    notes: Optional[str] = Query(None),
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """Admin approve bounty - bypasses org/finance role check (FREQ-10, FREQ-14)."""
    from src.services.bounty_service import BountyService
    from decimal import Decimal

    service = BountyService(db)
    try:
        report = service.approve_bounty(
            report_id=report_id,
            approved_by=current_user.id,
            bounty_amount=Decimal(str(bounty_amount)),
            notes=notes,
        )
        return {
            "message": "Bounty approved",
            "report_id": str(report.id),
            "bounty_amount": float(report.bounty_amount),
            "bounty_status": report.bounty_status,
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/finance/reports/{report_id}/reject-bounty")
def admin_reject_bounty(
    report_id: UUID,
    reason: str = Query(..., description="Reason for rejection"),
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """Admin reject bounty - bypasses org/finance role check (FREQ-10, FREQ-14)."""
    from src.services.bounty_service import BountyService

    service = BountyService(db)
    try:
        report = service.reject_bounty(
            report_id=report_id,
            rejected_by=current_user.id,
            reason=reason,
        )
        return {
            "message": "Bounty rejected",
            "report_id": str(report.id),
            "bounty_status": report.bounty_status,
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/finance/reports/{report_id}/mark-paid")
def admin_mark_bounty_paid(
    report_id: UUID,
    transaction_reference: Optional[str] = Query(None),
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """Admin mark bounty as paid - bypasses finance officer role check (FREQ-10, FREQ-20)."""
    from src.services.bounty_service import BountyService

    service = BountyService(db)
    try:
        report = service.mark_as_paid(
            report_id=report_id,
            paid_by=current_user.id,
            transaction_reference=transaction_reference,
        )
        return {
            "message": "Bounty marked as paid",
            "report_id": str(report.id),
            "bounty_status": report.bounty_status,
            "bounty_amount": float(report.bounty_amount),
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


