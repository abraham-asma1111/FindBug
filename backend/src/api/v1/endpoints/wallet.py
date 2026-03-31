"""Wallet API Endpoints - FREQ-20, FREQ-40."""
from typing import Optional
from uuid import UUID
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.core.database import get_db
from src.api.v1.middlewares.auth import get_current_user
from src.domain.models.user import User, UserRole
from src.services.wallet_service import WalletService

router = APIRouter(prefix="/wallet", tags=["wallet"])


class WithdrawRequest(BaseModel):
    """Withdraw request schema."""
    amount: float
    payment_method: str
    account_details: dict


@router.get("/balance", status_code=status.HTTP_200_OK)
def get_wallet_balance(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get wallet balance for current user - FREQ-40.
    
    Returns balance, reserved balance, and available balance.
    """
    service = WalletService(db)
    
    # Determine owner type based on role
    if current_user.role == UserRole.RESEARCHER:
        owner_id = current_user.researcher.id
        owner_type = "researcher"
    elif current_user.role == UserRole.ORGANIZATION:
        owner_id = current_user.organization.id
        owner_type = "organization"
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only researchers and organizations have wallets"
        )
    
    balance_info = service.get_balance(owner_id, owner_type)
    
    return balance_info


@router.post("/withdraw", status_code=status.HTTP_201_CREATED)
def withdraw_from_wallet(
    request: WithdrawRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Withdraw funds from wallet - FREQ-40.
    
    Only researchers can withdraw funds.
    Minimum withdrawal: 100 ETB
    """
    # Only researchers can withdraw
    if current_user.role != UserRole.RESEARCHER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only researchers can withdraw funds"
        )
    
    # Validate minimum withdrawal
    if request.amount < 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Minimum withdrawal amount is 100 ETB"
        )
    
    service = WalletService(db)
    
    try:
        # Generate saga ID for transaction
        from uuid import uuid4
        saga_id = str(uuid4())
        
        # Debit wallet
        result = service.debit_wallet(
            owner_id=current_user.researcher.id,
            owner_type="researcher",
            amount=Decimal(str(request.amount)),
            saga_id=saga_id,
            from_reserved=False,
            reference_type="withdrawal",
            reference_id=None
        )
        
        return {
            "message": "Withdrawal request submitted successfully",
            "transaction_id": result["transaction_id"],
            "amount": request.amount,
            "payment_method": request.payment_method,
            "new_balance": result["new_balance"],
            "status": "pending"
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process withdrawal: {str(e)}"
        )


@router.get("/transactions", status_code=status.HTTP_200_OK)
def get_wallet_transactions(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get wallet transaction history - FREQ-40.
    """
    service = WalletService(db)
    
    # Determine owner type based on role
    if current_user.role == UserRole.RESEARCHER:
        owner_id = current_user.researcher.id
        owner_type = "researcher"
    elif current_user.role == UserRole.ORGANIZATION:
        owner_id = current_user.organization.id
        owner_type = "organization"
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only researchers and organizations have wallets"
        )
    
    transactions = service.get_transaction_history(
        owner_id=owner_id,
        owner_type=owner_type,
        limit=limit,
        offset=offset
    )
    
    return {
        "transactions": transactions,
        "total": len(transactions),
        "limit": limit,
        "offset": offset
    }
