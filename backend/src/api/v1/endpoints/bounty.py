"""Bounty Approval and Payout API Endpoints - FREQ-10."""
from typing import Optional
from uuid import UUID
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.api.v1.middlewares.auth import get_current_user
from src.domain.models.user import User
from src.services.bounty_service import BountyService
from src.api.v1.schemas.report import BountyApproval


router = APIRouter()


@router.get("/reports/{report_id}/bounty/calculate", status_code=status.HTTP_200_OK)
def calculate_bounty(
    report_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Calculate bounty amount for a report - BR-05.
    
    Returns suggested bounty based on severity and reward tiers.
    Includes platform commission calculation (30%) - BR-06.
    
    Only organizations and finance officers can calculate.
    """
    if current_user.role not in ["organization", "finance_officer", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organizations or finance officers can calculate bounties"
        )
    
    service = BountyService(db)
    
    try:
        calculation = service.calculate_bounty_amount(report_id=report_id)
        return calculation
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/reports/{report_id}/bounty/approve", status_code=status.HTTP_200_OK)
@router.get("/reports/{report_id}/bounty/approve", status_code=status.HTTP_200_OK)
def approve_bounty(
    report_id: UUID,
    bounty_amount: Decimal = Query(..., description="Bounty amount to approve", gt=0),
    notes: Optional[str] = Query(None, description="Approval notes"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Approve bounty for a validated report - FREQ-10, UC-05.
    
    Pre-condition: Report status must be 'valid'
    Post-condition: Bounty approved, payout status set to 'pending'
    
    Business Rules:
    - BR-05: Amount must be within reward tier range
    - BR-07: Duplicates within 24h get 50%, after 24h get nothing
    - BR-08: Must be paid within 30 days
    
    Only organizations and finance officers can approve.
    """
    if current_user.role not in ["organization", "finance_officer", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organizations or finance officers can approve bounties"
        )
    
    service = BountyService(db)
    
    try:
        report = service.approve_bounty(
            report_id=report_id,
            approved_by=current_user.id,
            bounty_amount=bounty_amount,
            notes=notes
        )
        
        return {
            "message": "Bounty approved successfully",
            "report_id": str(report.id),
            "bounty_amount": float(report.bounty_amount),
            "bounty_status": report.bounty_status,
            "approved_at": report.bounty_approved_at
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/reports/{report_id}/bounty/reject", status_code=status.HTTP_200_OK)
@router.get("/reports/{report_id}/bounty/reject", status_code=status.HTTP_200_OK)
def reject_bounty(
    report_id: UUID,
    reason: str = Query(..., description="Reason for rejection"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Reject bounty for a report - FREQ-10.
    
    Used when report doesn't meet bounty criteria.
    
    Only organizations and finance officers can reject.
    """
    if current_user.role not in ["organization", "finance_officer", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organizations or finance officers can reject bounties"
        )
    
    service = BountyService(db)
    
    try:
        report = service.reject_bounty(
            report_id=report_id,
            rejected_by=current_user.id,
            reason=reason
        )
        
        return {
            "message": "Bounty rejected",
            "report_id": str(report.id),
            "bounty_status": report.bounty_status
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/reports/{report_id}/bounty/mark-paid", status_code=status.HTTP_200_OK)
@router.get("/reports/{report_id}/bounty/mark-paid", status_code=status.HTTP_200_OK)
def mark_bounty_paid(
    report_id: UUID,
    transaction_reference: Optional[str] = Query(None, description="Payment transaction reference"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark bounty as paid - FREQ-10, FREQ-20.
    
    Called after payment is processed through payment gateway.
    
    Only finance officers can mark as paid.
    """
    if current_user.role not in ["finance_officer", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only finance officers can mark bounties as paid"
        )
    
    service = BountyService(db)
    
    try:
        report = service.mark_as_paid(
            report_id=report_id,
            paid_by=current_user.id,
            transaction_reference=transaction_reference
        )
        
        return {
            "message": "Bounty marked as paid",
            "report_id": str(report.id),
            "bounty_status": report.bounty_status,
            "bounty_amount": float(report.bounty_amount)
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/bounty/pending-payouts", status_code=status.HTTP_200_OK)
def get_pending_payouts(
    program_id: Optional[UUID] = Query(None, description="Filter by program"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all reports with pending payouts - FREQ-20.
    
    Used by finance officers to process payments.
    Ordered by approval date (oldest first) - BR-08.
    
    Only finance officers can access.
    """
    if current_user.role not in ["finance_officer", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only finance officers can view pending payouts"
        )
    
    service = BountyService(db)
    
    reports = service.get_pending_payouts(
        program_id=program_id,
        limit=limit,
        offset=offset
    )
    
    return {
        "reports": reports,
        "total": len(reports),
        "limit": limit,
        "offset": offset
    }


@router.get("/bounty/overdue-payouts", status_code=status.HTTP_200_OK)
def get_overdue_payouts(
    days: int = Query(30, description="Days threshold for overdue (default: 30)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get overdue payouts - BR-08.
    
    Bounties must be processed within 30 days.
    Shows bounties that exceed the deadline.
    
    Only finance officers and admins can access.
    """
    if current_user.role not in ["finance_officer", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only finance officers can view overdue payouts"
        )
    
    service = BountyService(db)
    
    reports = service.get_overdue_payouts(days=days)
    
    return {
        "overdue_reports": reports,
        "total": len(reports),
        "threshold_days": days
    }


@router.get("/bounty/statistics", status_code=status.HTTP_200_OK)
def get_payout_statistics(
    program_id: Optional[UUID] = Query(None, description="Filter by program"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get payout statistics - FREQ-15, FREQ-20.
    
    Shows:
    - Total approved, paid, rejected bounties
    - Total amounts
    - Platform commission (30%) - BR-06
    
    Finance officers see all, organizations see their programs only.
    """
    if current_user.role not in ["organization", "finance_officer", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organizations or finance officers can view statistics"
        )
    
    # Organizations can only see their own programs
    if current_user.role == "organization" and not program_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organizations must specify a program_id"
        )
    
    service = BountyService(db)
    
    stats = service.get_payout_statistics(program_id=program_id)
    
    return stats
