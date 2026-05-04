"""
Subscription Service - FREQ-20 Dual Revenue Model.

Implements:
- Quarterly subscription billing (every 4 months, 3 times/year)
- Subscription tier management
- Automatic billing cycle management
- Overdue subscription tracking
"""
from typing import Dict, Any, Optional, List
from uuid import UUID, uuid4
from decimal import Decimal
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging

from sqlalchemy.orm import Session
from sqlalchemy import func

from src.domain.models.subscription import (
    OrganizationSubscription,
    SubscriptionPayment,
    SubscriptionTierPricing,
    SubscriptionTier,
    SubscriptionStatus
)
from src.domain.models.organization import Organization

logger = logging.getLogger(__name__)


class SubscriptionService:
    """
    Subscription service for dual revenue model.
    
    Revenue streams:
    1. Quarterly subscription fees (every 4 months)
    2. 30% commission on bounty payments (handled by EnhancedPayoutService)
    """
    
    BILLING_CYCLE_MONTHS = 4  # Quarterly billing every 4 months
    PAYMENTS_PER_YEAR = 3  # 3 payments per year
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_subscription(
        self,
        organization_id: UUID,
        tier: SubscriptionTier,
        start_date: Optional[datetime] = None,
        trial_days: int = 0,
        pay_from_wallet: bool = False
    ) -> OrganizationSubscription:
        """
        Create new subscription for organization.
        
        Args:
            organization_id: Organization ID
            tier: Subscription tier (basic, professional, enterprise)
            start_date: Subscription start date (default: now)
            trial_days: Trial period in days (default: 0)
            pay_from_wallet: If True, automatically pay from organization wallet
            
        Returns:
            OrganizationSubscription instance
        """
        # Get tier pricing
        tier_pricing = self.db.query(SubscriptionTierPricing).filter(
            SubscriptionTierPricing.tier == tier,
            SubscriptionTierPricing.is_active == True
        ).first()
        
        if not tier_pricing:
            raise ValueError(f"Tier '{tier}' not found or inactive")
        
        # Verify organization exists
        org = self.db.query(Organization).filter(
            Organization.id == organization_id
        ).first()
        
        if not org:
            raise ValueError("Organization not found")
        
        # Check for existing active subscription
        existing = self.db.query(OrganizationSubscription).filter(
            OrganizationSubscription.organization_id == organization_id,
            OrganizationSubscription.status.in_([
                SubscriptionStatus.ACTIVE,
                SubscriptionStatus.PENDING
            ])
        ).first()
        
        if existing:
            raise ValueError("Organization already has an active subscription")
        
        # Calculate dates
        if not start_date:
            start_date = datetime.utcnow()
        
        current_period_start = start_date
        current_period_end = start_date + relativedelta(months=self.BILLING_CYCLE_MONTHS)
        next_billing_date = current_period_end
        
        # Handle trial period
        is_trial = trial_days > 0
        trial_end_date = None
        if is_trial:
            trial_end_date = start_date + timedelta(days=trial_days)
            next_billing_date = trial_end_date
        
        # Create subscription
        subscription = OrganizationSubscription(
            organization_id=organization_id,
            tier=tier,
            status=SubscriptionStatus.PENDING,  # Always start as PENDING
            subscription_fee=tier_pricing.quarterly_price,
            currency=tier_pricing.currency,
            billing_cycle_months=self.BILLING_CYCLE_MONTHS,
            payments_per_year=self.PAYMENTS_PER_YEAR,
            start_date=start_date,
            current_period_start=current_period_start,
            current_period_end=current_period_end,
            next_billing_date=next_billing_date,
            trial_end_date=trial_end_date,
            is_trial=is_trial,
            features={
                "max_programs": int(tier_pricing.max_programs) if tier_pricing.max_programs is not None else None,
                "max_researchers": int(tier_pricing.max_researchers) if tier_pricing.max_researchers is not None else None,
                "max_reports_per_month": int(tier_pricing.max_reports_per_month) if tier_pricing.max_reports_per_month is not None else None,
                "ptaas_enabled": bool(tier_pricing.ptaas_enabled),
                "code_review_enabled": bool(tier_pricing.code_review_enabled),
                "ai_red_teaming_enabled": bool(tier_pricing.ai_red_teaming_enabled),
                "live_events_enabled": bool(tier_pricing.live_events_enabled),
                "ssdlc_integration_enabled": bool(tier_pricing.ssdlc_integration_enabled),
                "support_level": str(tier_pricing.support_level) if tier_pricing.support_level else None
            }
        )
        
        self.db.add(subscription)
        self.db.commit()
        self.db.refresh(subscription)
        
        logger.info(
            f"Created subscription {subscription.subscription_id} for org {organization_id}: "
            f"tier={tier}, fee={tier_pricing.quarterly_price}, trial={is_trial}"
        )
        
        # Create first payment record
        payment = self._create_payment_record(subscription)
        
        # If pay_from_wallet is True, automatically pay from wallet
        if pay_from_wallet:
            try:
                from src.services.wallet_service import WalletService
                wallet_service = WalletService(self.db)
                
                # CRITICAL FIX: Get user_id from organization
                # Wallets are stored with user_id as owner_id, not organization_id
                user_id = org.user_id
                
                # Check wallet balance using user_id
                wallet = wallet_service.get_or_create_wallet(user_id, "organization")
                if wallet.available_balance >= tier_pricing.quarterly_price:
                    # Deduct from wallet using user_id
                    wallet_service.deduct_from_wallet(
                        organization_id=user_id,  # Use user_id, not organization_id
                        amount=tier_pricing.quarterly_price,
                        description=f"Subscription payment - {tier} tier",
                        reference_type="subscription_payment",
                        reference_id=str(payment.payment_id)
                    )
                    
                    # Mark payment as paid
                    self.mark_payment_paid(
                        payment_id=payment.payment_id,
                        payment_method="wallet",
                        gateway_transaction_id=f"WALLET-{payment.payment_id.hex[:8].upper()}"
                    )
                    
                    logger.info(f"Subscription payment auto-paid from wallet for org {organization_id}")
                else:
                    logger.warning(
                        f"Insufficient wallet balance for org {organization_id}: "
                        f"required={tier_pricing.quarterly_price}, available={wallet.available_balance}"
                    )
            except Exception as e:
                logger.error(f"Failed to auto-pay from wallet: {str(e)}")
                # Don't fail subscription creation, just log the error
        
        return subscription
    
    def _create_payment_record(
        self,
        subscription: OrganizationSubscription
    ) -> SubscriptionPayment:
        """
        Create payment record for billing period.
        
        Args:
            subscription: OrganizationSubscription instance
            
        Returns:
            SubscriptionPayment instance
        """
        # Generate invoice number
        invoice_number = f"SUB-{subscription.subscription_id.hex[:8].upper()}-{datetime.utcnow().strftime('%Y%m')}"
        
        # CRITICAL FIX: For the first payment, due date should be NOW (immediate payment required)
        # For renewal payments, due date is next_billing_date
        # Check if this is the first payment by looking at subscription status
        if subscription.status == SubscriptionStatus.PENDING:
            # First payment - due immediately
            due_date = datetime.utcnow()
        else:
            # Renewal payment - due at next billing date
            due_date = subscription.next_billing_date
        
        payment = SubscriptionPayment(
            subscription_id=subscription.subscription_id,
            organization_id=subscription.organization_id,
            amount=subscription.subscription_fee,
            currency=subscription.currency,
            period_start=subscription.current_period_start,
            period_end=subscription.current_period_end,
            status="pending",
            due_date=due_date,
            invoice_number=invoice_number
        )
        
        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)
        
        logger.info(
            f"Created payment record {payment.payment_id} for subscription {subscription.subscription_id}: "
            f"amount={payment.amount}, due={payment.due_date}"
        )
        
        return payment
    
    def process_subscription_renewal(
        self,
        subscription_id: UUID
    ) -> OrganizationSubscription:
        """
        Process subscription renewal (move to next billing cycle).
        
        Called when payment is successful.
        
        Args:
            subscription_id: Subscription ID
            
        Returns:
            Updated subscription
        """
        subscription = self.db.query(OrganizationSubscription).filter(
            OrganizationSubscription.subscription_id == subscription_id
        ).first()
        
        if not subscription:
            raise ValueError("Subscription not found")
        
        # Move to next billing period
        subscription.current_period_start = subscription.current_period_end
        subscription.current_period_end = subscription.current_period_end + relativedelta(
            months=self.BILLING_CYCLE_MONTHS
        )
        subscription.next_billing_date = subscription.current_period_end
        subscription.status = SubscriptionStatus.ACTIVE
        subscription.is_trial = False
        subscription.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(subscription)
        
        logger.info(
            f"Renewed subscription {subscription_id}: "
            f"next_billing={subscription.next_billing_date}"
        )
        
        # Create next payment record
        self._create_payment_record(subscription)
        
        return subscription
    
    def mark_payment_paid(
        self,
        payment_id: UUID,
        payment_method: str,
        gateway_transaction_id: Optional[str] = None,
        gateway_response: Optional[Dict] = None
    ) -> SubscriptionPayment:
        """
        Mark subscription payment as paid.
        
        If payment was created with wallet payment method, deduct from wallet now.
        
        Args:
            payment_id: Payment ID
            payment_method: Payment method used (from Finance Officer)
            gateway_transaction_id: Gateway transaction ID
            gateway_response: Gateway response data
            
        Returns:
            Updated payment
        """
        payment = self.db.query(SubscriptionPayment).filter(
            SubscriptionPayment.payment_id == payment_id
        ).first()
        
        if not payment:
            raise ValueError("Payment not found")
        
        # CRITICAL FIX: Prevent duplicate verification
        if payment.status == "paid":
            raise ValueError("Payment has already been verified and marked as paid")
        
        # Check if this payment should be paid from wallet
        should_pay_from_wallet = payment.payment_method == "wallet_pending"
        
        # If payment should be from wallet, deduct now
        if should_pay_from_wallet:
            try:
                from src.services.wallet_service import WalletService
                wallet_service = WalletService(self.db)
                
                # Get organization to get user_id
                org = self.db.query(Organization).filter(
                    Organization.id == payment.organization_id
                ).first()
                
                if not org:
                    raise ValueError("Organization not found")
                
                # Get user_id from organization
                user_id = org.user_id
                
                # Check wallet balance
                wallet = wallet_service.get_or_create_wallet(user_id, "organization")
                if wallet.available_balance < payment.amount:
                    raise ValueError(
                        f"Insufficient wallet balance. Required: {payment.amount} ETB, "
                        f"Available: {wallet.available_balance} ETB"
                    )
                
                # Deduct from wallet
                wallet_service.deduct_from_wallet(
                    organization_id=user_id,  # Use user_id, not organization_id
                    amount=payment.amount,
                    description=f"Subscription payment - {payment.invoice_number}",
                    reference_type="subscription_payment",
                    reference_id=str(payment.payment_id)
                )
                
                logger.info(
                    f"Deducted {payment.amount} ETB from wallet for payment {payment_id}"
                )
                
                # Override payment method to show it was paid from wallet
                payment_method = "wallet"
                if not gateway_transaction_id:
                    gateway_transaction_id = f"WALLET-{payment.payment_id.hex[:8].upper()}"
                
            except Exception as e:
                logger.error(f"Failed to deduct from wallet: {str(e)}")
                raise ValueError(f"Failed to process wallet payment: {str(e)}")
        
        # Update payment
        payment.status = "paid"
        payment.paid_at = datetime.utcnow()
        payment.payment_method = payment_method
        payment.gateway_transaction_id = gateway_transaction_id
        payment.gateway_response = gateway_response
        payment.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(payment)
        
        logger.info(f"Marked payment {payment_id} as paid via {payment_method}")
        
        # Process subscription renewal
        self.process_subscription_renewal(payment.subscription_id)
        
        return payment
    
    def cancel_subscription(
        self,
        subscription_id: UUID,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Cancel subscription by deleting it from database.
        This allows users to freely choose a new plan afterwards.
        
        Args:
            subscription_id: Subscription ID
            reason: Cancellation reason (logged but not stored)
            
        Returns:
            Dict with cancellation confirmation
        """
        subscription = self.db.query(OrganizationSubscription).filter(
            OrganizationSubscription.subscription_id == subscription_id
        ).first()
        
        if not subscription:
            raise ValueError("Subscription not found")
        
        # Store info for logging before deletion
        org_id = subscription.organization_id
        tier = subscription.tier
        
        # Delete the subscription
        self.db.delete(subscription)
        self.db.commit()
        
        logger.info(
            f"Deleted subscription {subscription_id} for org {org_id}: "
            f"tier={tier}, reason={reason}"
        )
        
        return {
            "message": "Subscription cancelled successfully",
            "subscription_id": str(subscription_id),
            "organization_id": str(org_id),
            "cancelled_tier": tier,
            "reason": reason
        }
    
    def get_overdue_subscriptions(self) -> List[Dict[str, Any]]:
        """
        Get subscriptions with overdue payments.
        
        Returns:
            List of overdue subscriptions
        """
        now = datetime.utcnow()
        
        overdue_payments = self.db.query(SubscriptionPayment).filter(
            SubscriptionPayment.status == "pending",
            SubscriptionPayment.due_date < now
        ).all()
        
        result = []
        for payment in overdue_payments:
            subscription = self.db.query(OrganizationSubscription).filter(
                OrganizationSubscription.subscription_id == payment.subscription_id
            ).first()
            
            if subscription:
                days_overdue = (now - payment.due_date).days
                
                result.append({
                    "subscription_id": str(subscription.subscription_id),
                    "organization_id": str(subscription.organization_id),
                    "payment_id": str(payment.payment_id),
                    "amount": float(payment.amount),
                    "due_date": payment.due_date,
                    "days_overdue": days_overdue,
                    "tier": subscription.tier,
                    "status": subscription.status
                })
        
        return result
    
    def suspend_overdue_subscriptions(self, days_threshold: int = 7) -> int:
        """
        Suspend subscriptions with payments overdue by threshold.
        
        Args:
            days_threshold: Days overdue before suspension
            
        Returns:
            Number of subscriptions suspended
        """
        overdue = self.get_overdue_subscriptions()
        suspended_count = 0
        
        for item in overdue:
            if item["days_overdue"] >= days_threshold:
                subscription = self.db.query(OrganizationSubscription).filter(
                    OrganizationSubscription.subscription_id == UUID(item["subscription_id"])
                ).first()
                
                if subscription and subscription.status == SubscriptionStatus.ACTIVE:
                    subscription.status = SubscriptionStatus.SUSPENDED
                    subscription.updated_at = datetime.utcnow()
                    suspended_count += 1
                    
                    logger.warning(
                        f"Suspended subscription {subscription.subscription_id} "
                        f"(overdue by {item['days_overdue']} days)"
                    )
        
        if suspended_count > 0:
            self.db.commit()
        
        return suspended_count
    
    def get_subscription_revenue_report(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get subscription revenue report.
        
        Args:
            start_date: Report start date
            end_date: Report end date
            
        Returns:
            Revenue report
        """
        query = self.db.query(SubscriptionPayment).filter(
            SubscriptionPayment.status == "paid"
        )
        
        if start_date:
            query = query.filter(SubscriptionPayment.paid_at >= start_date)
        if end_date:
            query = query.filter(SubscriptionPayment.paid_at <= end_date)
        
        payments = query.all()
        
        total_revenue = sum(p.amount for p in payments)
        payment_count = len(payments)
        
        # Group by tier
        tier_revenue = {}
        for payment in payments:
            subscription = self.db.query(OrganizationSubscription).filter(
                OrganizationSubscription.subscription_id == payment.subscription_id
            ).first()
            
            if subscription:
                tier = subscription.tier
                if tier not in tier_revenue:
                    tier_revenue[tier] = {"count": 0, "revenue": Decimal("0")}
                
                tier_revenue[tier]["count"] += 1
                tier_revenue[tier]["revenue"] += payment.amount
        
        return {
            "total_revenue": float(total_revenue),
            "payment_count": payment_count,
            "average_payment": float(total_revenue / payment_count) if payment_count > 0 else 0,
            "by_tier": {
                tier: {
                    "count": data["count"],
                    "revenue": float(data["revenue"]),
                    "average": float(data["revenue"] / data["count"]) if data["count"] > 0 else 0
                }
                for tier, data in tier_revenue.items()
            },
            "period": {
                "start": start_date,
                "end": end_date
            }
        }
    
    def seed_tier_pricing(self):
        """Seed default subscription tier pricing."""
        tiers = [
            {
                "tier": SubscriptionTier.BASIC,
                "name": "Basic",
                "description": "Essential bug bounty features for small teams",
                "quarterly_price": Decimal("15000.00"),  # ETB
                "max_programs": 3,
                "max_researchers": 50,
                "max_reports_per_month": 20,
                "ptaas_enabled": False,
                "code_review_enabled": False,
                "ai_red_teaming_enabled": False,
                "live_events_enabled": False,
                "ssdlc_integration_enabled": False,
                "support_level": "email"
            },
            {
                "tier": SubscriptionTier.PROFESSIONAL,
                "name": "Professional",
                "description": "Advanced features for growing security programs",
                "quarterly_price": Decimal("45000.00"),  # ETB
                "max_programs": 10,
                "max_researchers": 200,
                "max_reports_per_month": 100,
                "ptaas_enabled": True,
                "code_review_enabled": True,
                "ai_red_teaming_enabled": False,
                "live_events_enabled": True,
                "ssdlc_integration_enabled": True,
                "support_level": "priority"
            },
            {
                "tier": SubscriptionTier.ENTERPRISE,
                "name": "Enterprise",
                "description": "Complete platform access with dedicated support",
                "quarterly_price": Decimal("120000.00"),  # ETB
                "max_programs": None,  # Unlimited
                "max_researchers": None,  # Unlimited
                "max_reports_per_month": None,  # Unlimited
                "ptaas_enabled": True,
                "code_review_enabled": True,
                "ai_red_teaming_enabled": True,
                "live_events_enabled": True,
                "ssdlc_integration_enabled": True,
                "support_level": "dedicated"
            }
        ]
        
        for tier_data in tiers:
            existing = self.db.query(SubscriptionTierPricing).filter(
                SubscriptionTierPricing.tier == tier_data["tier"]
            ).first()
            
            if not existing:
                pricing = SubscriptionTierPricing(**tier_data)
                self.db.add(pricing)
                logger.info(f"Seeded tier pricing: {tier_data['name']}")
        
        self.db.commit()
