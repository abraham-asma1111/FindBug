"""
Payment API Schemas
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID


class PaymentMethodCreate(BaseModel):
    """Schema for creating payment method"""
    method_type: str  # telebirr, cbe_birr, bank_transfer
    account_number: Optional[str] = None
    account_name: Optional[str] = None
    bank_name: Optional[str] = None
    phone_number: Optional[str] = None
    is_default: Optional[bool] = False


class PaymentMethodResponse(BaseModel):
    """Schema for payment method response"""
    id: UUID
    user_id: UUID
    method_type: str
    account_number: Optional[str] = None
    account_name: Optional[str] = None
    bank_name: Optional[str] = None
    phone_number: Optional[str] = None
    is_default: bool
    is_verified: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PaymentMethodUpdate(BaseModel):
    """Schema for updating payment method"""
    account_number: Optional[str] = None
    account_name: Optional[str] = None
    bank_name: Optional[str] = None
    phone_number: Optional[str] = None
    is_default: Optional[bool] = None
