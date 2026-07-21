"""
Finance Settings Endpoints — API routes for finance configuration
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from src.core.database import get_db
from src.domain.models.user import User
from src.core.dependencies import require_financial

router = APIRouter(prefix="/finance/settings", tags=["Finance Settings"])


class FeeSettingsUpdate(BaseModel):
    commission_rate: Optional[float] = None
    processing_fee: Optional[float] = None
    minimum_payout: Optional[float] = None


@router.get(
    "/fees",
    summary="Get Fee Settings",
    description="Get current fee configuration (Admin/Finance Officer only)"
)
async def get_fee_settings(
    current_user: User = Depends(require_financial),
    db: Session = Depends(get_db)
):
    """Get current fee settings."""
    # In production, this would fetch from a settings table
    return {
        "commission_rate": 15.0,
        "processing_fee": 2.5,
        "minimum_payout": 50.0,
        "currency": "USD"
    }


@router.put(
    "/fees",
    summary="Update Fee Settings",
    description="Update fee configuration (Admin/Finance Officer only)"
)
async def update_fee_settings(
    settings: FeeSettingsUpdate,
    current_user: User = Depends(require_financial),
    db: Session = Depends(get_db)
):
    """Update fee settings."""
    # In production, this would update a settings table
    return {
        "message": "Fee settings updated successfully",
        "settings": {
            "commission_rate": settings.commission_rate or 15.0,
            "processing_fee": settings.processing_fee or 2.5,
            "minimum_payout": settings.minimum_payout or 50.0
        }
    }
