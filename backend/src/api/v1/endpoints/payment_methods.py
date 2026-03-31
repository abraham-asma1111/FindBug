"""
Payment Methods API Endpoints - Fix for missing 404 endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict
from uuid import UUID

from src.core.database import get_db
from src.services.payment_service import PaymentService
from ..schemas.payment import PaymentMethodCreate, PaymentMethodResponse

router = APIRouter(prefix="/payment-methods", tags=["Payment Methods"])

@router.get("/{user_id}", response_model=List[PaymentMethodResponse])
async def get_payment_methods(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    """Get user's payment methods"""
    try:
        service = PaymentService(db)
        methods = service.get_user_payment_methods(str(user_id))
        return [PaymentMethodResponse.from_orm(method) for method in methods]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/{user_id}", response_model=PaymentMethodResponse)
async def add_payment_method(
    user_id: UUID,
    method_data: PaymentMethodCreate,
    db: Session = Depends(get_db)
):
    """Add new payment method"""
    try:
        service = PaymentService(db)
        method = service.add_payment_method(str(user_id), method_data.dict())
        return PaymentMethodResponse.from_orm(method)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put("/{method_id}")
async def update_payment_method(
    method_id: UUID,
    method_data: Dict,
    db: Session = Depends(get_db)
):
    """Update payment method"""
    try:
        service = PaymentService(db)
        method = service.update_payment_method(str(method_id), method_data)
        if not method:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment method not found"
            )
        return PaymentMethodResponse.from_orm(method)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/{method_id}")
async def delete_payment_method(
    method_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete payment method"""
    try:
        service = PaymentService(db)
        success = service.delete_payment_method(str(method_id))
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment method not found"
            )
        return {"message": "Payment method deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/{method_id}/set-default")
async def set_default_payment_method(
    method_id: UUID,
    user_id: UUID,
    db: Session = Depends(get_db)
):
    """Set default payment method"""
    try:
        service = PaymentService(db)
        success = service.set_default_payment_method(str(method_id), str(user_id))
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment method not found"
            )
        return {"message": "Default payment method updated successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
