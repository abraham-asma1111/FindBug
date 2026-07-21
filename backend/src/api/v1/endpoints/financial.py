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
from src.domain.models.organization import Organization
from src.services.subscription_service import SubscriptionService
from src.services.enhanced_payout_service import EnhancedPayoutService

router = APIRouter(prefix="/financial", tags=["financial"])


@router.get("/organizations")
def get_organizations_for_finance(
    limit: int = Query(default=100, le=1000),
    offset: int = Query(default=0),
    search: Optional[str] = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all organizations with subscription info for Finance Officers.
    
    Returns organization list with subscription details for financial monitoring.
    
    Requires: Finance Officer or Admin
    """
    # Authorization check - Finance Officer only
    if current_user.role not in [UserRole.FINANCE_OFFICER.value, "finance_officer"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only finance officers can view organizations"
        )
    
    # Build query with eager loading of user relationship
    from sqlalchemy.orm import joinedload
    query = db.query(Organization).options(joinedload(Organization.user))
    
    # Apply search filter
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Organization.company_name.ilike(search_term)) |
            (Organization.email.ilike(search_term))
        )
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    organizations = query.offset(offset).limit(limit).all()
    
    # Fetch subscription data for each organization
    result = []
    for org in organizations:
        # Get active subscription
        subscription = db.query(func.max).from_statement(
            db.query(func.max).select_from(func.max)
        ).first() if False else None  # Placeholder
        
        # Get subscription info from subscription table
        from src.domain.models.subscription import OrganizationSubscription
        subscription = db.query(OrganizationSubscription).filter(
            OrganizationSubscription.organization_id == org.id
        ).first()
        
        org_data = {
            "id": str(org.id),
            "company_name": org.company_name,
            "name": org.company_name,
            "industry": org.industry if org.industry else None,
            "email": org.user.email if org.user else None,
            "website": org.website,
            "created_at": org.created_at.isoformat() if org.created_at else None,
            "is_verified": org.domain_verified if hasattr(org, 'domain_verified') else False,
        }
        
        # Add subscription info if exists
        if subscription:
            org_data.update({
                "subscription_type": subscription.tier,
                "subscription_amount": float(subscription.subscription_fee),
                "subscription_status": subscription.status.lower(),
                "subscription_start_date": subscription.start_date.isoformat() if subscription.start_date else None,
                "next_billing_date": subscription.next_billing_date.isoformat() if subscription.next_billing_date else None,
            })
        else:
            org_data.update({
                "subscription_type": "free",
                "subscription_amount": 0,
                "subscription_status": "inactive",
                "subscription_start_date": None,
                "next_billing_date": None,
            })
        
        result.append(org_data)
    
    return {
        "organizations": result,
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.get("/organizations/{organization_id}")
def get_organization_details_for_finance(
    organization_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed organization information for Finance Officers.
    
    Includes subscription details, payment history, and program statistics.
    
    Requires: Finance Officer or Admin
    """
    # Authorization check - Finance Officer only
    if current_user.role not in [UserRole.FINANCE_OFFICER.value, "finance_officer"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only finance officers can view organization details"
        )
    
    # Get organization
    from uuid import UUID
    try:
        org_uuid = UUID(organization_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid organization ID format"
        )
    
    # Get organization with eager loading
    from sqlalchemy.orm import joinedload
    organization = db.query(Organization).options(
        joinedload(Organization.user)
    ).filter(Organization.id == org_uuid).first()
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    # Get subscription
    from src.domain.models.subscription import OrganizationSubscription
    subscription = db.query(OrganizationSubscription).filter(
        OrganizationSubscription.organization_id == org_uuid
    ).first()
    
    # Get program count
    from src.domain.models.program import BountyProgram
    program_count = db.query(func.count(BountyProgram.id)).filter(
        BountyProgram.organization_id == org_uuid
    ).scalar() or 0
    
    # Get report count
    from src.domain.models.report import VulnerabilityReport
    report_count = db.query(func.count(VulnerabilityReport.id)).join(
        BountyProgram, VulnerabilityReport.program_id == BountyProgram.id
    ).filter(
        BountyProgram.organization_id == org_uuid
    ).scalar() or 0
    
    # Get total bounties paid
    total_bounties = db.query(func.sum(BountyPayment.total_amount)).join(
        VulnerabilityReport, BountyPayment.report_id == VulnerabilityReport.id
    ).join(
        BountyProgram, VulnerabilityReport.program_id == BountyProgram.id
    ).filter(
        BountyProgram.organization_id == org_uuid,
        BountyPayment.status == 'completed'
    ).scalar() or 0
    
    # Build branding object - always return object, never null
    branding_data = {
        "logo_url": getattr(organization, 'logo_url', None),
        "cover_image_url": getattr(organization, 'cover_image_url', None),
        "brand_color": getattr(organization, 'brand_color', None),
        "theme_settings": getattr(organization, 'theme_settings', None),
    }
    
    # If all branding fields are None, still return the object structure
    # This ensures frontend can safely access branding properties
    
    # Build subscription object
    subscription_data = None
    if subscription:
        subscription_data = {
            "tier": subscription.tier,
            "status": subscription.status.lower(),
            "subscription_fee": float(subscription.subscription_fee),
            "start_date": subscription.start_date.isoformat() if subscription.start_date else None,
            "current_period_start": subscription.current_period_start.isoformat() if hasattr(subscription, 'current_period_start') and subscription.current_period_start else None,
            "current_period_end": subscription.current_period_end.isoformat() if hasattr(subscription, 'current_period_end') and subscription.current_period_end else None,
            "next_billing_date": subscription.next_billing_date.isoformat() if subscription.next_billing_date else None,
            "billing_cycle_months": subscription.billing_cycle_months if hasattr(subscription, 'billing_cycle_months') else 4,
        }
    
    return {
        "id": str(organization.id),
        "company_name": organization.company_name,
        "industry": organization.industry,
        "email": organization.user.email if organization.user else None,
        "website": organization.website,
        "created_at": organization.created_at.isoformat() if organization.created_at else None,
        "is_verified": getattr(organization, 'domain_verified', False),
        "program_count": program_count,
        "report_count": report_count,
        "total_bounties_paid": float(total_bounties),
        "branding": branding_data,
        "subscription": subscription_data
    }


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
    # Authorization check - Finance Officer only
    if current_user.role not in [UserRole.FINANCE_OFFICER.value, "finance_officer"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only finance officers can view financial reports"
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
    # Authorization check - Finance Officer only
    if current_user.role not in [UserRole.FINANCE_OFFICER.value, "finance_officer"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only finance officers can view commission reports"
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
    # Authorization check - Finance Officer only
    if current_user.role not in [UserRole.FINANCE_OFFICER.value, "finance_officer"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only finance officers can view pending payments"
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
    # Authorization check - Finance Officer only
    if current_user.role not in [UserRole.FINANCE_OFFICER.value, "finance_officer"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only finance officers can view overdue payments"
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
