"""
Bounty Payment Endpoints for Finance Officer
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from src.core.database import get_db
from src.domain.models.user import User, UserRole
from src.domain.models.bounty_payment import BountyPayment
from src.domain.models.report import VulnerabilityReport
from src.domain.models.researcher import Researcher
from src.domain.models.organization import Organization
from src.api.v1.middlewares.auth import get_current_user

router = APIRouter(prefix="/bounty-payments", tags=["Bounty Payments"])


@router.get("", status_code=status.HTTP_200_OK)
def list_bounty_payments(
    status_filter: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List bounty payments with optional status filter.
    
    Status options: pending, approved, completed, rejected
    If no status provided, returns all payments.
    
    Only Finance Officers and Admins can access this endpoint.
    """
    # Check permissions
    if current_user.role.lower() not in [UserRole.FINANCE_OFFICER.value, UserRole.ADMIN.value, UserRole.SUPER_ADMIN.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Finance Officers and Admins can view bounty payments"
        )
    
    # Build query
    query = db.query(BountyPayment)
    
    # Apply status filter if provided
    if status_filter:
        query = query.filter(BountyPayment.status == status_filter)
    
    # Order by most recent first
    payments = query.order_by(BountyPayment.created_at.desc()).all()
    
    # Enrich with related data
    result = []
    for payment in payments:
        # Get report
        report = db.query(VulnerabilityReport).filter(
            VulnerabilityReport.id == payment.report_id
        ).first()
        
        # Get researcher
        researcher = db.query(Researcher).filter(
            Researcher.id == payment.researcher_id
        ).first()
        
        # Get organization
        organization = db.query(Organization).filter(
            Organization.id == payment.organization_id
        ).first()
        
        result.append({
            "payment_id": str(payment.payment_id),
            "transaction_id": payment.transaction_id,
            "status": payment.status,
            "report": {
                "id": str(report.id) if report else None,
                "report_number": report.report_number if report else None,
                "title": report.title if report else None,
                "severity": report.assigned_severity if report else None
            },
            "researcher": {
                "id": str(researcher.id) if researcher else None,
                "username": researcher.username if researcher else "Unknown"
            },
            "organization": {
                "id": str(organization.id) if organization else None,
                "name": organization.company_name if organization else "Unknown"
            },
            "researcher_amount": float(payment.researcher_amount),
            "commission_amount": float(payment.commission_amount),
            "total_amount": float(payment.total_amount),
            "approved_at": payment.approved_at.isoformat() if payment.approved_at else None,
            "completed_at": payment.completed_at.isoformat() if payment.completed_at else None,
            "created_at": payment.created_at.isoformat() if payment.created_at else None
        })
    
    return {
        "bounty_payments": result,
        "total": len(result)
    }


@router.get("/approved", status_code=status.HTTP_200_OK)
def list_approved_bounty_payments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all approved bounty payments for Finance Officer to process.
    
    Only Finance Officers and Admins can access this endpoint.
    """
    # Check permissions
    if current_user.role.lower() not in [UserRole.FINANCE_OFFICER.value, UserRole.ADMIN.value, UserRole.SUPER_ADMIN.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Finance Officers and Admins can view approved bounty payments"
        )
    
    # Get all approved bounty payments
    approved_payments = db.query(BountyPayment).filter(
        BountyPayment.status == "approved"
    ).order_by(BountyPayment.approved_at.desc()).all()
    
    # Enrich with related data
    result = []
    for payment in approved_payments:
        # Get report
        report = db.query(VulnerabilityReport).filter(
            VulnerabilityReport.id == payment.report_id
        ).first()
        
        # Get researcher
        researcher = db.query(Researcher).filter(
            Researcher.id == payment.researcher_id
        ).first()
        
        # Get organization
        organization = db.query(Organization).filter(
            Organization.id == payment.organization_id
        ).first()
        
        result.append({
            "payment_id": str(payment.payment_id),
            "transaction_id": payment.transaction_id,
            "status": payment.status,
            "report": {
                "id": str(report.id) if report else None,
                "report_number": report.report_number if report else None,
                "title": report.title if report else None,
                "severity": report.assigned_severity if report else None
            },
            "researcher": {
                "id": str(researcher.id) if researcher else None,
                "username": researcher.username if researcher else "Unknown"
            },
            "organization": {
                "id": str(organization.id) if organization else None,
                "name": organization.company_name if organization else "Unknown"
            },
            "researcher_amount": float(payment.researcher_amount),
            "commission_amount": float(payment.commission_amount),
            "total_amount": float(payment.total_amount),
            "approved_at": payment.approved_at.isoformat() if payment.approved_at else None,
            "created_at": payment.created_at.isoformat() if payment.created_at else None
        })
    
    return {
        "bounty_payments": result,
        "total": len(result)
    }


@router.post("/process/{payment_id}", status_code=status.HTTP_200_OK)
def process_bounty_payment(
    payment_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Process an approved bounty payment.
    
    This transfers the researcher_amount to the researcher's wallet
    and keeps the commission in the platform wallet.
    
    Only Finance Officers and Admins can process payments.
    """
    # Check permissions
    if current_user.role.lower() not in [UserRole.FINANCE_OFFICER.value, UserRole.ADMIN.value, UserRole.SUPER_ADMIN.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Finance Officers and Admins can process bounty payments"
        )
    
    # Get the bounty payment
    payment = db.query(BountyPayment).filter(
        BountyPayment.payment_id == payment_id
    ).first()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bounty payment not found"
        )
    
    # Verify payment is approved
    if payment.status != "approved":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payment status is '{payment.status}', expected 'approved'"
        )
    
    try:
        from src.services.wallet_service import WalletService
        from src.services.payment_service import PaymentService
        from decimal import Decimal
        from datetime import datetime
        import uuid
        
        wallet_service = WalletService(db)
        payment_service = PaymentService(db)
        
        # Generate saga ID for this transaction
        saga_id = f"PROCESS-{uuid.uuid4().hex[:12].upper()}"
        
        # Step 1: Get researcher's user_id
        researcher = db.query(Researcher).filter(
            Researcher.id == payment.researcher_id
        ).first()
        
        if not researcher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Researcher not found"
            )
        
        # Step 2: Credit researcher wallet
        wallet_service.credit_wallet(
            owner_id=researcher.user_id,  # Use user_id, not researcher_id
            owner_type="researcher",
            amount=Decimal(str(payment.researcher_amount)),
            saga_id=saga_id,
            reference_type="bounty_payment",
            reference_id=payment.payment_id
        )
        
        # Step 3: Debit platform wallet (only researcher_amount, commission stays)
        # Get platform user (first admin or finance officer)
        from src.domain.models.user import User as UserModel
        platform_user = db.query(UserModel).filter(UserModel.role == "admin").first()
        if not platform_user:
            platform_user = db.query(UserModel).filter(UserModel.role == "finance_officer").first()
        
        if not platform_user:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Platform wallet user not found"
            )
        
        wallet_service.debit_wallet(
            owner_id=platform_user.id,
            owner_type="platform",
            amount=Decimal(str(payment.researcher_amount)),
            saga_id=saga_id,
            from_reserved=False,
            reference_type="bounty_payment",
            reference_id=payment.payment_id
        )
        
        # Step 4: Update payment status
        payment.status = "completed"
        payment.completed_at = datetime.utcnow()
        db.commit()
        db.refresh(payment)
        
        return {
            "message": "Bounty payment processed successfully",
            "payment_id": str(payment.payment_id),
            "researcher_amount": float(payment.researcher_amount),
            "commission_kept": float(payment.commission_amount),
            "status": payment.status
        }
    
    except ValueError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process payment: {str(e)}"
        )
