"""Organization Subscription models - Dual Revenue Model."""
from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import (
    Column, String, DateTime, Numeric, Boolean,
    ForeignKey, func, Index, Enum as SQLEnum
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSON
from sqlalchemy.orm import relationship
import enum

from src.core.database import Base


class SubscriptionTier(str, enum.Enum):
    """Subscription tier levels."""
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class SubscriptionStatus(str, enum.Enum):
    """Subscription status."""
    ACTIVE = "active"
    PENDING = "pending"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    SUSPENDED = "suspended"


class OrganizationSubscription(Base):
    """
    Organization Subscription model.
    
    Dual Revenue Model:
    1. Subscription fee (quarterly: every 4 months, 3 times/year)
    2. 30% commission on each bounty payment
    """
    
    __tablename__ = "organization_subscriptions"
    
    subscription_id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    organization_id = Column(PGUUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    
    # Subscription details
    tier = Column(SQLEnum(SubscriptionTier), nullable=False, server_default="basic")
    status = Column(SQLEnum(SubscriptionStatus), nullable=False, server_default="pending")
    
    # Pricing
    subscription_fee = Column(Numeric(15, 2), nullable=False)  # Quarterly fee
    currency = Column(String(3), nullable=False, server_default="ETB")
    
    # Billing cycle (quarterly: every 4 months)
    billing_cycle_months = Column(Numeric(3, 0), nullable=False, server_default="4")  # 4 months
    payments_per_year = Column(Numeric(2, 0), nullable=False, server_default="3")  # 3 times/year
    
    # Subscription period
    start_date = Column(DateTime(timezone=True), nullable=False)
    current_period_start = Column(DateTime(timezone=True), nullable=False)
    current_period_end = Column(DateTime(timezone=True), nullable=False)
    next_billing_date = Column(DateTime(timezone=True), nullable=False)
    
    # Cancellation
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    cancellation_reason = Column(String(500), nullable=True)
    
    # Trial period
    trial_end_date = Column(DateTime(timezone=True), nullable=True)
    is_trial = Column(Boolean, nullable=False, server_default="false")
    
    # Features (JSON for flexibility)
    features = Column(JSON, nullable=True)
    # Example: {"max_programs": 10, "max_researchers": 100, "ptaas_enabled": true}
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    organization = relationship("Organization")
    payments = relationship("SubscriptionPayment", back_populates="subscription", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('ix_org_subscriptions_organization_id', 'organization_id'),
        Index('ix_org_subscriptions_status', 'status'),
        Index('ix_org_subscriptions_next_billing_date', 'next_billing_date'),
    )


class SubscriptionPayment(Base):
    """
    Subscription Payment model.
    
    Tracks quarterly subscription payments (separate from bounty commissions).
    """
    
    __tablename__ = "subscription_payments"
    
    payment_id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    subscription_id = Column(PGUUID(as_uuid=True), ForeignKey("organization_subscriptions.subscription_id", ondelete="CASCADE"), nullable=False)
    organization_id = Column(PGUUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    
    # Payment details
    amount = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(3), nullable=False, server_default="ETB")
    
    # Billing period
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    
    # Payment status
    status = Column(String(50), nullable=False, server_default="pending")
    # Status: pending, paid, failed, refunded
    
    # Payment method
    payment_method = Column(String(50), nullable=True)
    payment_gateway = Column(String(50), nullable=True)
    gateway_transaction_id = Column(String(200), nullable=True)
    gateway_response = Column(JSON, nullable=True)
    
    # Timeline
    due_date = Column(DateTime(timezone=True), nullable=False)
    paid_at = Column(DateTime(timezone=True), nullable=True)
    failed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Failure handling
    failure_reason = Column(String(500), nullable=True)
    retry_count = Column(Numeric(3, 0), nullable=False, server_default="0")
    
    # Invoice
    invoice_number = Column(String(100), nullable=True)
    invoice_url = Column(String(500), nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    subscription = relationship("OrganizationSubscription", back_populates="payments")
    organization = relationship("Organization")
    
    # Indexes
    __table_args__ = (
        Index('ix_subscription_payments_subscription_id', 'subscription_id'),
        Index('ix_subscription_payments_organization_id', 'organization_id'),
        Index('ix_subscription_payments_status', 'status'),
        Index('ix_subscription_payments_due_date', 'due_date'),
    )


class SubscriptionTierPricing(Base):
    """
    Subscription Tier Pricing model.
    
    Defines pricing and features for each subscription tier.
    """
    
    __tablename__ = "subscription_tier_pricing"
    
    pricing_id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Tier details
    tier = Column(SQLEnum(SubscriptionTier), nullable=False, unique=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    
    # Pricing (quarterly)
    quarterly_price = Column(Numeric(15, 2), nullable=False)
    annual_price = Column(Numeric(15, 2), nullable=True)  # Optional: if they pay yearly
    currency = Column(String(3), nullable=False, server_default="ETB")
    
    # Features
    max_programs = Column(Numeric(5, 0), nullable=True)  # null = unlimited
    max_researchers = Column(Numeric(6, 0), nullable=True)  # null = unlimited
    max_reports_per_month = Column(Numeric(6, 0), nullable=True)
    
    # Feature flags
    ptaas_enabled = Column(Boolean, nullable=False, server_default="false")
    code_review_enabled = Column(Boolean, nullable=False, server_default="false")
    ai_red_teaming_enabled = Column(Boolean, nullable=False, server_default="false")
    live_events_enabled = Column(Boolean, nullable=False, server_default="false")
    ssdlc_integration_enabled = Column(Boolean, nullable=False, server_default="false")
    
    # Support level
    support_level = Column(String(50), nullable=False, server_default="email")
    # email, priority, dedicated
    
    # Additional features (JSON)
    features = Column(JSON, nullable=True)
    
    # Active flag
    is_active = Column(Boolean, nullable=False, server_default="true")
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Indexes
    __table_args__ = (
        Index('ix_subscription_tier_pricing_tier', 'tier'),
    )
