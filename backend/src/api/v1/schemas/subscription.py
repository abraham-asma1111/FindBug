"""Subscription API schemas."""
from typing import Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, Field


class SubscriptionTierPricingResponse(BaseModel):
    """Subscription tier pricing response."""
    pricing_id: UUID
    tier: str
    name: str
    description: Optional[str]
    quarterly_price: Decimal
    annual_price: Optional[Decimal]
    currency: str
    max_programs: Optional[int]
    max_researchers: Optional[int]
    max_reports_per_month: Optional[int]
    ptaas_enabled: bool
    code_review_enabled: bool
    ai_red_teaming_enabled: bool
    live_events_enabled: bool
    ssdlc_integration_enabled: bool
    support_level: str
    features: Optional[Dict[str, Any]]
    is_active: bool
    
    class Config:
        from_attributes = True


class CreateSubscriptionRequest(BaseModel):
    """Create subscription request."""
    organization_id: UUID
    tier: str = Field(..., description="basic, professional, or enterprise")
    trial_days: int = Field(default=0, ge=0, le=90)
    pay_from_wallet: bool = Field(default=False, description="Automatically pay from organization wallet")


class SubscriptionResponse(BaseModel):
    """Subscription response."""
    subscription_id: UUID
    organization_id: UUID
    tier: str
    status: str
    subscription_fee: Decimal
    currency: str
    billing_cycle_months: int
    payments_per_year: int
    start_date: datetime
    current_period_start: datetime
    current_period_end: datetime
    next_billing_date: datetime
    cancelled_at: Optional[datetime]
    cancellation_reason: Optional[str]
    trial_end_date: Optional[datetime]
    is_trial: bool
    features: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SubscriptionPaymentResponse(BaseModel):
    """Subscription payment response."""
    payment_id: UUID
    subscription_id: UUID
    organization_id: UUID
    amount: Decimal
    currency: str
    period_start: datetime
    period_end: datetime
    status: str
    payment_method: Optional[str]
    payment_gateway: Optional[str]
    gateway_transaction_id: Optional[str]
    due_date: datetime
    paid_at: Optional[datetime]
    failed_at: Optional[datetime]
    failure_reason: Optional[str]
    retry_count: int
    invoice_number: Optional[str]
    invoice_url: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class MarkPaymentPaidRequest(BaseModel):
    """Mark payment as paid request."""
    payment_method: str
    gateway_transaction_id: Optional[str] = None
    gateway_response: Optional[Dict[str, Any]] = None


class CancelSubscriptionRequest(BaseModel):
    """Cancel subscription request."""
    reason: Optional[str] = None


class ChangeSubscriptionPlanRequest(BaseModel):
    """Change subscription plan request."""
    new_tier: str  # 'basic', 'professional', 'enterprise'


class SubscriptionRevenueReport(BaseModel):
    """Subscription revenue report."""
    total_revenue: float
    payment_count: int
    average_payment: float
    by_tier: Dict[str, Dict[str, Any]]
    period: Dict[str, Optional[datetime]]
