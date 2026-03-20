"""Financial Reporting API endpoints - Dual Revenue Model."""
from typing import Optional
from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from src.core.database import get_db
from src.api.v1.middlewares.auth import get_current_user
from src.domain.models.user import User, UserRole
from src.domain.models.bounty_payment import BountyPayment
from src.domain.models.subscription import SubscriptionPayment
from src.services.subscription_service import SubscriptionService
from src.services.enhanced_payout_service import EnhancedPayoutService

router = APIRouter(prefix="/financial", tags=["financial"])


@router.get("/revenue-summary")
def get_revenue_summary(
    start_date: Optional[datetime] = Query(default=None),
    end_date: Optional[datetime] = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive revenue summary (subscriptions + commissions).
    
    Dual Revenue Model:
    1. Subscription fees (quarterly)
    2. Bounty commissions (30% per transaction)
    
    Requires: Admin or Finance Officer
    """
    # Authorization check
    if current_user.role not in [UserRole.ADMIN, UserRole.STAFF]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and finance officers can view financial reports"
        )
    
    # Get subscription revenue
    subscription_service = SubscriptionService(db)
    subscription_report = subscription_service.get_subscription_revenue_report(
        start_date=start_date,
        end_date=end_date
    )
    
    # Get commission revenue
    commission_query = db.query(
        func.sum(BountyPayment.commission_amount).label('total_commission'),
        func.count(BountyPayment.payment_id).label('payment_count')
    ).filter(
        BountyPayment.status == 'completed'
    )
    
    if start_date:
        commission_query = commission_query.filter(BountyPayment.completed_at >= start_date)
    if end_date:
        commission_query = commission_query.filter(BountyPayment.completed_at <= end_date)
    
    commission_result = commission_query.first()
    total_commission = commission_result.total_commission or Decimal("0")
    commission_count = commission_result.payment_count or 0
    
    # Calculate totals
    total_subscription_revenue = Decimal(str(subscription_report["total_revenue"]))
    total_revenue = total_subscription_revenue + total_commission
    
    return {
        "period": {
            "start": start_date,
            "end": end_date
        },
        "subscription_revenue": {
            "total": float(total_subscription_revenue),
            "payment_count": subscription_report["payment_count"],
            "average_payment": subscription_report["average_payment"],
            "by_tier": subscription_report["by_tier"]
        },
        "commission_revenue": {
            "total": float(total_commission),
            "payment_count": commission_count,
            "average_commission": float(total_commission / commission_count) if commission_count > 0 else 0
        },
        "total_revenue": float(total_revenue),
        "revenue_breakdown": {
            "subscription_percentage": float((total_subscription_revenue / total_revenue * 100)) if total_revenue > 0 else 0,
            "commission_percentage": float((total_commission / total_revenue * 100)) if total_revenue > 0 else 0
        }
    }


@router.get("/commission-report")
def get_commission_report(
    start_date: Optional[datetime] = Query(default=None),
    end_date: Optional[datetime] = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed commission revenue report.
    
    Shows 30% commission earned from bounty payments.
    
    Requires: Admin or Finance Officer
    """
    # Authorization check
    if current_user.role not in [UserRole.ADMIN, UserRole.STAFF]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and finance officers can view commission reports"
        )
    
    # Query completed payments
    query = db.query(BountyPayment).filter(
        BountyPayment.status == 'completed'
    )
    
    if start_date:
        query = query.filter(BountyPayment.completed_at >= start_date)
    if end_date:
        query = query.filter(BountyPayment.completed_at <= end_date)
    
    payments = query.all()
    
    # Calculate statistics
    total_researcher_amount = sum(p.researcher_amount for p in payments)
    total_commission = sum(p.commission_amount for p in payments)
    total_organization_paid = sum(p.total_amount for p in payments)
    payment_count = len(payments)
    
    return {
        "period": {
            "start": start_date,
            "end": end_date
        },
        "summary": {
            "payment_count": payment_count,
            "total_researcher_amount": float(total_researcher_amount),
            "total_commission": float(total_commission),
            "total_organization_paid": float(total_organization_paid),
            "average_commission": float(total_commission / payment_count) if payment_count > 0 else 0,
            "commission_rate": "30%"
        },
        "payments": [
            {
                "payment_id": str(p.payment_id),
                "transaction_id": p.transaction_id,
                "researcher_amount": float(p.researcher_amount),
                "commission_amount": float(p.commission_amount),
                "total_amount": float(p.total_amount),
                "completed_at": p.completed_at,
                "payment_method": p.payment_method
            }
            for p in payments[:50]  # Limit to 50 for performance
        ]
    }


@router.get("/pending-payments")
def get_pending_payments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all pending payments (subscriptions + bounties).
    
    Requires: Admin or Finance Officer
    """
    # Authorization check
    if current_user.role not in [UserRole.ADMIN, UserRole.STAFF]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and finance officers can view pending payments"
        )
    
    # Get pending subscription payments
    pending_subscriptions = db.query(SubscriptionPayment).filter(
        SubscriptionPayment.status == 'pending'
    ).order_by(SubscriptionPayment.due_date.asc()).all()
    
    # Get pending bounty payments
    pending_bounties = db.query(BountyPayment).filter(
        BountyPayment.status.in_(['approved', 'processing'])
    ).order_by(BountyPayment.approved_at.asc()).all()
    
    # Calculate totals
    total_subscription_pending = sum(p.amount for p in pending_subscriptions)
    total_bounty_pending = sum(p.total_amount for p in pending_bounties)
    
    return {
        "subscription_payments": {
            "count": len(pending_subscriptions),
            "total_amount": float(total_subscription_pending),
            "payments": [
                {
                    "payment_id": str(p.payment_id),
                    "organization_id": str(p.organization_id),
                    "amount": float(p.amount),
                    "due_date": p.due_date,
                    "invoice_number": p.invoice_number
                }
                for p in pending_subscriptions
            ]
        },
        "bounty_payments": {
            "count": len(pending_bounties),
            "total_amount": float(total_bounty_pending),
            "payments": [
                {
                    "payment_id": str(p.payment_id),
                    "transaction_id": p.transaction_id,
                    "researcher_amount": float(p.researcher_amount),
                    "commission_amount": float(p.commission_amount),
                    "total_amount": float(p.total_amount),
                    "status": p.status,
                    "approved_at": p.approved_at,
                    "payout_deadline": p.payout_deadline
                }
                for p in pending_bounties
            ]
        },
        "total_pending": float(total_subscription_pending + total_bounty_pending)
    }


@router.get("/overdue-payments")
def get_overdue_payments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all overdue payments (subscriptions + bounties).
    
    Requires: Admin or Finance Officer
    """
    # Authorization check
    if current_user.role not in [UserRole.ADMIN, UserRole.STAFF]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and finance officers can view overdue payments"
        )
    
    now = datetime.utcnow()
    
    # Get overdue subscription payments
    subscription_service = SubscriptionService(db)
    overdue_subscriptions = subscription_service.get_overdue_subscriptions()
    
    # Get overdue bounty payments
    payout_service = EnhancedPayoutService(db)
    overdue_bounties = payout_service.get_overdue_payments()
    
    return {
        "subscription_payments": {
            "count": len(overdue_subscriptions),
            "payments": overdue_subscriptions
        },
        "bounty_payments": {
            "count": len(overdue_bounties),
            "payments": overdue_bounties
        },
        "total_overdue_count": len(overdue_subscriptions) + len(overdue_bounties)
    }
