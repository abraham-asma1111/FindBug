"""Subscription API endpoints - FREQ-20 Dual Revenue Model."""
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from src.core.database import get_db
from src.api.v1.middlewares.auth import get_current_user
from src.domain.models.user import User, UserRole
from src.domain.models.subscription import (
    OrganizationSubscription,
    SubscriptionPayment,
    SubscriptionTierPricing
)
from src.services.subscription_service import SubscriptionService
from src.api.v1.schemas.subscription import (
    SubscriptionTierPricingResponse,
    CreateSubscriptionRequest,
    SubscriptionResponse,
    SubscriptionPaymentResponse,
    MarkPaymentPaidRequest,
    CancelSubscriptionRequest,
    ChangeSubscriptionPlanRequest,
    SubscriptionRevenueReport
)

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


@router.get("/tiers", response_model=List[SubscriptionTierPricingResponse])
def get_subscription_tiers(
    db: Session = Depends(get_db)
):
    """
    Get all available subscription tiers.
    
    Public endpoint - no authentication required.
    """
    tiers = db.query(SubscriptionTierPricing).filter(
        SubscriptionTierPricing.is_active == True
    ).all()
    
    return tiers


@router.post("", response_model=SubscriptionResponse, status_code=status.HTTP_201_CREATED)
def create_subscription(
    request: CreateSubscriptionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create new subscription for organization.
    
    Requires: Admin or Organization role
    """
    # Authorization check
    user_role_lower = current_user.role.lower()
    if user_role_lower not in [UserRole.ADMIN.value, UserRole.ORGANIZATION.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and organizations can create subscriptions"
        )
    
    # If organization role, verify they're creating for their own org
    if user_role_lower == UserRole.ORGANIZATION.value:
        # Get the organization for this user
        from src.domain.models.organization import Organization
        user_org = db.query(Organization).filter(
            Organization.user_id == current_user.id
        ).first()
        
        if not user_org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization profile not found"
            )
        
        if user_org.id != request.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Organizations can only create subscriptions for themselves"
            )
    
    try:
        service = SubscriptionService(db)
        subscription = service.create_subscription(
            organization_id=request.organization_id,
            tier=request.tier,
            trial_days=request.trial_days,
            pay_from_wallet=request.pay_from_wallet
        )
        return subscription
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/current", response_model=SubscriptionResponse)
def get_current_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's subscription.
    
    For organizations: returns their own subscription
    For other roles: returns error
    """
    # Only organizations have subscriptions
    # ROLE COMPARISON FIX: Compare with enum.value (string) not enum object
    if current_user.role.lower() != UserRole.ORGANIZATION.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organizations have subscriptions"
        )
    
    # Get organization from user
    from src.domain.models.organization import Organization
    organization = db.query(Organization).filter(
        Organization.user_id == current_user.id
    ).first()
    
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization profile not found"
        )
    
    subscription = db.query(OrganizationSubscription).filter(
        OrganizationSubscription.organization_id == organization.id,
        or_(
            func.upper(OrganizationSubscription.status) == 'ACTIVE',
            func.upper(OrganizationSubscription.status) == 'PENDING',
            func.upper(OrganizationSubscription.status) == 'SUSPENDED'
        )
    ).first()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found"
        )
    
    return subscription


@router.get("/organization/{organization_id}", response_model=SubscriptionResponse)
def get_organization_subscription(
    organization_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get active subscription for organization.
    
    Requires: Admin, Organization (own), or Staff
    """
    # Authorization check
    user_role_lower = current_user.role.lower()
    if user_role_lower == UserRole.ORGANIZATION.value:
        # Get organization from user
        from src.domain.models.organization import Organization
        organization = db.query(Organization).filter(
            Organization.user_id == current_user.id
        ).first()
        
        if not organization or organization.id != organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Organizations can only view their own subscription"
            )
    elif user_role_lower not in [UserRole.ADMIN.value, UserRole.STAFF.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    subscription = db.query(OrganizationSubscription).filter(
        OrganizationSubscription.organization_id == organization_id,
        or_(
            func.upper(OrganizationSubscription.status) == 'ACTIVE',
            func.upper(OrganizationSubscription.status) == 'PENDING',
            func.upper(OrganizationSubscription.status) == 'SUSPENDED'
        )
    ).first()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found"
        )
    
    return subscription


@router.get("/{subscription_id}/payments", response_model=List[SubscriptionPaymentResponse])
def get_subscription_payments(
    subscription_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0)
):
    """
    Get payment history for subscription.
    
    Requires: Admin, Organization (own), or Finance Officer
    """
    # Get subscription
    subscription = db.query(OrganizationSubscription).filter(
        OrganizationSubscription.subscription_id == subscription_id
    ).first()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )
    
    # Authorization check
    user_role_lower = current_user.role.lower()
    if user_role_lower == UserRole.ORGANIZATION.value:
        # Get organization from user
        from src.domain.models.organization import Organization
        organization = db.query(Organization).filter(
            Organization.user_id == current_user.id
        ).first()
        
        if not organization or organization.id != subscription.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Organizations can only view their own payments"
            )
    elif user_role_lower not in [UserRole.ADMIN.value, UserRole.STAFF.value, UserRole.FINANCE_OFFICER.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    # For organizations, only show paid payments (actual payment history)
    # For finance officers/admins, show all payments
    if user_role_lower == UserRole.ORGANIZATION.value:
        payments = db.query(SubscriptionPayment).filter(
            SubscriptionPayment.subscription_id == subscription_id,
            SubscriptionPayment.status == "paid"  # Only show completed payments
        ).order_by(
            SubscriptionPayment.created_at.desc()
        ).limit(limit).offset(offset).all()
    else:
        # Finance officers and admins see all payments
        payments = db.query(SubscriptionPayment).filter(
            SubscriptionPayment.subscription_id == subscription_id
        ).order_by(
            SubscriptionPayment.created_at.desc()
        ).limit(limit).offset(offset).all()
    
    return payments


@router.post("/payments/{payment_id}/mark-paid", response_model=SubscriptionPaymentResponse)
def mark_payment_paid(
    payment_id: UUID,
    request: MarkPaymentPaidRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark subscription payment as paid.
    
    Requires: Admin or Finance Officer
    """
    # Authorization check
    user_role_lower = current_user.role.lower()
    if user_role_lower not in [UserRole.ADMIN.value, UserRole.STAFF.value, UserRole.FINANCE_OFFICER.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and finance officers can mark payments as paid"
        )
    
    try:
        service = SubscriptionService(db)
        payment = service.mark_payment_paid(
            payment_id=payment_id,
            payment_method=request.payment_method,
            gateway_transaction_id=request.gateway_transaction_id,
            gateway_response=request.gateway_response
        )
        return payment
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{subscription_id}/cancel", response_model=dict)
def cancel_subscription(
    subscription_id: UUID,
    request: CancelSubscriptionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cancel subscription by deleting it.
    This allows the organization to freely choose a new plan afterwards.
    
    Requires: Admin or Organization (own)
    """
    # Get subscription
    subscription = db.query(OrganizationSubscription).filter(
        OrganizationSubscription.subscription_id == subscription_id
    ).first()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )
    
    # Authorization check
    user_role_lower = current_user.role.lower()
    if user_role_lower == UserRole.ORGANIZATION.value:
        # Get organization from user
        from src.domain.models.organization import Organization
        organization = db.query(Organization).filter(
            Organization.user_id == current_user.id
        ).first()
        
        if not organization or organization.id != subscription.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Organizations can only cancel their own subscription"
            )
    elif user_role_lower != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    try:
        service = SubscriptionService(db)
        result = service.cancel_subscription(
            subscription_id=subscription_id,
            reason=request.reason
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{subscription_id}/change-plan", response_model=SubscriptionResponse)
def change_subscription_plan(
    subscription_id: UUID,
    request: ChangeSubscriptionPlanRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change subscription plan/tier.
    
    Requires: Admin or Organization (own)
    """
    # Get subscription
    subscription = db.query(OrganizationSubscription).filter(
        OrganizationSubscription.subscription_id == subscription_id
    ).first()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )
    
    # Authorization check
    user_role_lower = current_user.role.lower()
    if user_role_lower == UserRole.ORGANIZATION.value:
        # Get organization from user
        from src.domain.models.organization import Organization
        organization = db.query(Organization).filter(
            Organization.user_id == current_user.id
        ).first()
        
        if not organization or organization.id != subscription.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Organizations can only change their own subscription"
            )
    elif user_role_lower != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    # Validate new tier
    valid_tiers = ['basic', 'professional', 'enterprise']
    if request.new_tier.lower() not in valid_tiers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid tier. Must be one of: {', '.join(valid_tiers)}"
        )
    
    # Check if already on this tier
    if subscription.tier.lower() == request.new_tier.lower():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already subscribed to this tier"
        )
    
    # Get tier pricing
    tier_pricing = db.query(SubscriptionTierPricing).filter(
        SubscriptionTierPricing.tier == request.new_tier.upper(),
        SubscriptionTierPricing.is_active == True
    ).first()
    
    if not tier_pricing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pricing not found for tier: {request.new_tier}"
        )
    
    # Update subscription
    subscription.tier = request.new_tier.upper()
    subscription.subscription_fee = tier_pricing.quarterly_price
    subscription.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(subscription)
    
    return subscription


@router.get("/overdue", response_model=List[dict])
def get_overdue_subscriptions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get subscriptions with overdue payments.
    
    Requires: Admin or Finance Officer
    """
    # Authorization check
    user_role_lower = current_user.role.lower()
    if user_role_lower not in [UserRole.ADMIN.value, UserRole.STAFF.value, UserRole.FINANCE_OFFICER.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and finance officers can view overdue subscriptions"
        )
    
    service = SubscriptionService(db)
    overdue = service.get_overdue_subscriptions()
    
    return overdue


@router.get("/pending-payments", response_model=dict)
def get_pending_payments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all pending subscription payments awaiting verification.
    Only shows payments that are due now or overdue (not future payments).
    
    Requires: Admin or Finance Officer
    """
    # Authorization check
    user_role_lower = current_user.role.lower()
    if user_role_lower not in [UserRole.ADMIN.value, UserRole.STAFF.value, UserRole.FINANCE_OFFICER.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and finance officers can view pending payments"
        )
    
    # Get all pending payments that are due now or overdue
    # This excludes future payments that were just created for the next billing cycle
    from src.domain.models.organization import Organization
    now = datetime.utcnow()
    
    pending_payments = db.query(SubscriptionPayment).filter(
        SubscriptionPayment.status == "pending",
        SubscriptionPayment.due_date <= now  # Only show payments that are due now or overdue
    ).all()
    
    result = []
    for payment in pending_payments:
        # Get subscription
        subscription = db.query(OrganizationSubscription).filter(
            OrganizationSubscription.subscription_id == payment.subscription_id
        ).first()
        
        if subscription:
            # Get organization
            organization = db.query(Organization).filter(
                Organization.id == subscription.organization_id
            ).first()
            
            result.append({
                "payment_id": str(payment.payment_id),
                "subscription_id": str(subscription.subscription_id),
                "organization_id": str(subscription.organization_id),
                "organization_name": organization.company_name if organization else "Unknown",
                "amount": float(payment.amount),
                "currency": payment.currency,
                "tier": subscription.tier,
                "due_date": payment.due_date,
                "invoice_number": payment.invoice_number,
                "period_start": payment.period_start,
                "period_end": payment.period_end
            })
    
    return {"payments": result}


@router.get("/all", response_model=dict)
def get_all_subscriptions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    tier: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    search: Optional[str] = Query(default=None),
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0)
):
    """
    Get all subscriptions with filtering and search.
    
    Requires: Admin or Finance Officer
    """
    # Authorization check
    user_role_lower = current_user.role.lower()
    if user_role_lower not in [UserRole.ADMIN.value, UserRole.STAFF.value, UserRole.FINANCE_OFFICER.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and finance officers can view all subscriptions"
        )
    
    from src.domain.models.organization import Organization
    
    # Build query
    query = db.query(OrganizationSubscription).join(
        Organization,
        OrganizationSubscription.organization_id == Organization.id
    )
    
    # Apply filters
    if tier:
        query = query.filter(func.upper(OrganizationSubscription.tier) == tier.upper())
    
    if status:
        query = query.filter(func.upper(OrganizationSubscription.status) == status.upper())
    
    if search:
        query = query.filter(
            Organization.company_name.ilike(f"%{search}%")
        )
    
    # Get total count
    total = query.count()
    
    # Get paginated results
    subscriptions = query.order_by(
        OrganizationSubscription.created_at.desc()
    ).limit(limit).offset(offset).all()
    
    # Format results
    results = []
    for sub in subscriptions:
        org = db.query(Organization).filter(
            Organization.id == sub.organization_id
        ).first()
        
        results.append({
            "subscription_id": str(sub.subscription_id),
            "organization_id": str(sub.organization_id),
            "organization_name": org.company_name if org else "Unknown",
            "tier": sub.tier,
            "status": sub.status,
            "subscription_fee": float(sub.subscription_fee),
            "currency": sub.currency,
            "start_date": sub.start_date,
            "next_billing_date": sub.next_billing_date,
            "is_trial": sub.is_trial,
            "trial_end_date": sub.trial_end_date,
            "created_at": sub.created_at,
            "updated_at": sub.updated_at
        })
    
    return {
        "subscriptions": results,
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.get("/{subscription_id}/details", response_model=dict)
def get_subscription_details(
    subscription_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed subscription information including payment history.
    
    Requires: Admin or Finance Officer
    """
    # Authorization check
    user_role_lower = current_user.role.lower()
    if user_role_lower not in [UserRole.ADMIN.value, UserRole.STAFF.value, UserRole.FINANCE_OFFICER.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and finance officers can view subscription details"
        )
    
    from src.domain.models.organization import Organization
    
    # Get subscription
    subscription = db.query(OrganizationSubscription).filter(
        OrganizationSubscription.subscription_id == subscription_id
    ).first()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )
    
    # Get organization
    organization = db.query(Organization).filter(
        Organization.id == subscription.organization_id
    ).first()
    
    # Get payment history
    payments = db.query(SubscriptionPayment).filter(
        SubscriptionPayment.subscription_id == subscription_id
    ).order_by(SubscriptionPayment.created_at.desc()).all()
    
    payment_history = []
    for payment in payments:
        payment_history.append({
            "payment_id": str(payment.payment_id),
            "amount": float(payment.amount),
            "currency": payment.currency,
            "status": payment.status,
            "due_date": payment.due_date,
            "paid_at": payment.paid_at,
            "payment_method": payment.payment_method,
            "invoice_number": payment.invoice_number,
            "period_start": payment.period_start,
            "period_end": payment.period_end,
            "created_at": payment.created_at
        })
    
    return {
        "subscription": {
            "subscription_id": str(subscription.subscription_id),
            "organization_id": str(subscription.organization_id),
            "organization_name": organization.company_name if organization else "Unknown",
            "tier": subscription.tier,
            "status": subscription.status,
            "subscription_fee": float(subscription.subscription_fee),
            "currency": subscription.currency,
            "billing_cycle_months": subscription.billing_cycle_months,
            "payments_per_year": subscription.payments_per_year,
            "start_date": subscription.start_date,
            "current_period_start": subscription.current_period_start,
            "current_period_end": subscription.current_period_end,
            "next_billing_date": subscription.next_billing_date,
            "is_trial": subscription.is_trial,
            "trial_end_date": subscription.trial_end_date,
            "features": subscription.features,
            "created_at": subscription.created_at,
            "updated_at": subscription.updated_at
        },
        "organization": {
            "id": str(organization.id) if organization else None,
            "company_name": organization.company_name if organization else None,
            "email": organization.email if organization else None,
            "website": organization.website if organization else None
        } if organization else None,
        "payment_history": payment_history,
        "stats": {
            "total_payments": len(payments),
            "paid_payments": len([p for p in payments if p.status == "paid"]),
            "pending_payments": len([p for p in payments if p.status == "pending"]),
            "total_paid": float(sum(p.amount for p in payments if p.status == "paid"))
        }
    }


@router.get("/overdue", response_model=List[dict])
def get_overdue_subscriptions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get subscriptions with overdue payments.
    
    Requires: Admin or Finance Officer
    """
    # Authorization check
    user_role_lower = current_user.role.lower()
    if user_role_lower not in [UserRole.ADMIN.value, UserRole.STAFF.value, UserRole.FINANCE_OFFICER.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and finance officers can view overdue subscriptions"
        )
    
    service = SubscriptionService(db)
    overdue = service.get_overdue_subscriptions()
    
    return overdue


@router.post("/suspend-overdue", response_model=dict)
def suspend_overdue_subscriptions(
    days_threshold: int = Query(default=7, ge=1, le=30),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Suspend subscriptions with overdue payments.
    
    Requires: Admin only
    """
    # Authorization check
    if current_user.role.lower() != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can suspend subscriptions"
        )
    
    service = SubscriptionService(db)
    suspended_count = service.suspend_overdue_subscriptions(days_threshold)
    
    return {
        "suspended_count": suspended_count,
        "days_threshold": days_threshold
    }


@router.get("/revenue-report", response_model=SubscriptionRevenueReport)
def get_subscription_revenue_report(
    start_date: Optional[datetime] = Query(default=None),
    end_date: Optional[datetime] = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get subscription revenue report.
    
    Requires: Admin or Finance Officer
    """
    # Authorization check
    user_role_lower = current_user.role.lower()
    if user_role_lower not in [UserRole.ADMIN.value, UserRole.STAFF.value, UserRole.FINANCE_OFFICER.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and finance officers can view revenue reports"
        )
    
    service = SubscriptionService(db)
    report = service.get_subscription_revenue_report(
        start_date=start_date,
        end_date=end_date
    )
    
    return report


@router.post("/seed-tiers", response_model=dict)
def seed_subscription_tiers(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Seed default subscription tier pricing.
    
    Requires: Admin only
    """
    # Authorization check
    if current_user.role.lower() != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can seed tier pricing"
        )
    
    service = SubscriptionService(db)
    service.seed_tier_pricing()
    
    return {"message": "Subscription tiers seeded successfully"}
