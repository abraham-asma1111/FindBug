"""
Payment API Schemas
"""
from typing import Optional
from pydantic import BaseModel, Field


class PayoutRequestSchema(BaseModel):
    amount: float = Field(..., gt=0)
    payment_method: str
    payment_details: dict


class PayoutStatusResponse(BaseModel):
    payout_id: str
    amount: float
    status: str
    method: str
    created_at: str


class PaymentHistoryResponse(BaseModel):
    payment_id: str
    amount: float
    status: str
    created_at: str
    report_id: Optional[str] = None
