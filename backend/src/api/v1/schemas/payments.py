"""
Payment API Schemas — Request/Response models for payment endpoints
"""
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from decimal import Decimal


# ═══════════════════════════════════════════════════════════════════════
# BOUNTY PAYMENT SCHEMAS
# ═══════════════════════════════════════════════════════════════════════

class BountyPaymentCreateRequest(BaseModel):
    """Request to create bounty payment"""
    report_id: str = Field(..., description="Report ID")
    researcher_amount: Decimal = Field(..., gt=0, description="Amount for researcher (commission calculated automatically)")


class BountyPaymentProcessRequest(BaseModel):
    """Request to process bounty payment"""
    payment_method: str = Field(..., description="Payment method: telebirr, cbe_birr, bank_transfer")
    payment_gateway: str = Field(..., description="Payment gateway identifier")


class BountyPaymentCompleteRequest(BaseModel):
    """Request to complete bounty payment"""
    gateway_transaction_id: str = Field(..., description="External transaction ID from gateway")
    gateway_response: Optional[Dict[str, Any]] = Field(None, description="Gateway API response")


class BountyPaymentResponse(BaseModel):
    """Bounty payment response"""
    payment_id: str
    transaction_id: str
    report_id: str
    researcher_id: str
    researcher_amount: float
    commission_amount: float
    total_amount: float
    status: str
    payment_method: Optional[str] = None
    payment_gateway: Optional[str] = None
    gateway_transaction_id: Optional[str] = None
    payout_deadline: str
    completed_at: Optional[str] = None
    created_at: str


# ═══════════════════════════════════════════════════════════════════════
# PAYOUT REQUEST SCHEMAS
# ═══════════════════════════════════════════════════════════════════════

class PayoutRequestCreate(BaseModel):
    """Request to create payout"""
    amount: Decimal = Field(..., gt=0, description="Payout amount")
    payment_method: str = Field(..., description="Payment method: telebirr, cbe_birr, bank_transfer")
    payment_details: Dict[str, Any] = Field(..., description="Payment details (phone, account_number, etc.)")


class PayoutApprovalRequest(BaseModel):
    """Request to approve payout"""
    pass  # No additional fields needed


class PayoutRejectionRequest(BaseModel):
    """Request to reject payout"""
    reason: str = Field(..., description="Rejection reason")


class PayoutRequestResponse(BaseModel):
    """Payout request response"""
    payout_id: str
    researcher_id: str
    amount: float
    payment_method: str
    payment_details: Dict[str, Any]
    status: str
    failure_reason: Optional[str] = None
    created_at: str
    processed_at: Optional[str] = None


class PayoutListResponse(BaseModel):
    """List of payout requests"""
    payouts: List[PayoutRequestResponse]
    total: int


# ═══════════════════════════════════════════════════════════════════════
# PAYMENT GATEWAY SCHEMAS
# ═══════════════════════════════════════════════════════════════════════

class PaymentGatewayConfigRequest(BaseModel):
    """Request to configure payment gateway"""
    name: str = Field(..., description="Gateway name")
    gateway_type: str = Field(..., description="Gateway type: telebirr, cbe_birr, bank_transfer")
    config: Dict[str, Any] = Field(..., description="Gateway configuration (API keys, credentials)")
    is_active: bool = Field(True, description="Whether gateway is active")


class PaymentGatewayResponse(BaseModel):
    """Payment gateway response"""
    gateway_id: str
    name: str
    gateway_type: str
    is_active: bool
    created_at: str


# ═══════════════════════════════════════════════════════════════════════
# TRANSACTION SCHEMAS
# ═══════════════════════════════════════════════════════════════════════

class TransactionResponse(BaseModel):
    """Transaction response"""
    transaction_id: str
    user_id: str
    type: str
    amount: float
    status: str
    reference_id: Optional[str] = None
    reference_type: Optional[str] = None
    created_at: str


# ═══════════════════════════════════════════════════════════════════════
# PAYMENT HISTORY SCHEMAS
# ═══════════════════════════════════════════════════════════════════════

class PaymentHistoryResponse(BaseModel):
    """Payment history response"""
    history_id: str
    payment_id: str
    previous_status: str
    new_status: str
    changed_by: Optional[str] = None
    notes: Optional[str] = None
    changed_at: str


# ═══════════════════════════════════════════════════════════════════════
# LEGACY SCHEMAS (for backward compatibility)
# ═══════════════════════════════════════════════════════════════════════

class PayoutRequestSchema(BaseModel):
    """Legacy payout request schema"""
    amount: float = Field(..., gt=0)
    payment_method: str
    payment_details: dict


class PayoutStatusResponse(BaseModel):
    """Legacy payout status response"""
    payout_id: str
    amount: float
    status: str
    method: str
    created_at: str
