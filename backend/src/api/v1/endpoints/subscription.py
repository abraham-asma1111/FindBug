"""Subscription API endpoints - FREQ-20 Dual Revenue Model."""
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

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
    if current_user.role not in [UserRole.ADMIN, UserRole.ORGANIZATION]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and organizations can create subscriptions"
        )
    
    # If organization role, verify they're creating for their own org
    if current_user.role == UserRole.ORGANIZATION:
        if current_user.id != request.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Organizations can only create subscriptions for themselves"
            )
    
    try:
        service = SubscriptionService(db)
        subscription = service.create_subscription(
            organization_id=request.organization_id,
            tier=request.tier,
            trial_days=request.trial_days
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
    if current_user.role != UserRole.ORGANIZATION:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organizations have subscriptions"
        )
    
    subscription = db.query(OrganizationSubscription).filter(
        OrganizationSubscription.organization_id == current_user.organization.id,
        OrganizationSubscription.status.in_(["active", "pending", "suspended"])
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
    if current_user.role == UserRole.ORGANIZATION:
        if current_user.organization.id != organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Organizations can only view their own subscription"
            )
    elif current_user.role not in [UserRole.ADMIN, UserRole.STAFF]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    subscription = db.query(OrganizationSubscription).filter(
        OrganizationSubscription.organization_id == organization_id,
        OrganizationSubscription.status.in_(["active", "pending", "suspended"])
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
    if current_user.role == UserRole.ORGANIZATION:
        if current_user.id != subscription.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Organizations can only view their own payments"
            )
    elif current_user.role not in [UserRole.ADMIN, UserRole.STAFF]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
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
    if current_user.role not in [UserRole.ADMIN, UserRole.STAFF]:
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


@router.post("/{subscription_id}/cancel", response_model=SubscriptionResponse)
def cancel_subscription(
    subscription_id: UUID,
    request: CancelSubscriptionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cancel subscription.
    
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
    if current_user.role == UserRole.ORGANIZATION:
        if current_user.id != subscription.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Organizations can only cancel their own subscription"
            )
    elif current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    try:
        service = SubscriptionService(db)
        subscription = service.cancel_subscription(
            subscription_id=subscription_id,
            reason=request.reason
        )
        return subscription
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


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
    if current_user.role not in [UserRole.ADMIN, UserRole.STAFF]:
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
    if current_user.role != UserRole.ADMIN:
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
    if current_user.role not in [UserRole.ADMIN, UserRole.STAFF]:
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
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can seed tier pricing"
        )
    
    service = SubscriptionService(db)
    service.seed_tier_pricing()
    
    return {"message": "Subscription tiers seeded successfully"}
