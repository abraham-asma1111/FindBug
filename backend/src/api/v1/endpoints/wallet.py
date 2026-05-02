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
    # CRITICAL FIX: Use current_user.id (user ID), NOT researcher.id or organization.id
    # The wallets.owner_id foreign key references users.id
    # ROLE COMPARISON FIX: Compare with enum.value (string) not enum object
    if current_user.role.lower() == UserRole.RESEARCHER.value:
        owner_id = current_user.id
        owner_type = "researcher"
    elif current_user.role.lower() == UserRole.ORGANIZATION.value:
        owner_id = current_user.id
        owner_type = "organization"
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only researchers and organizations have wallets"
        )
    
    balance_info = service.get_balance(owner_id, owner_type)
    
    return balance_info


@router.post("/recharge", status_code=status.HTTP_201_CREATED)
def recharge_wallet(
    amount: float = Query(..., gt=0, description="Amount to recharge"),
    payment_method: str = Query(..., description="Payment method: bank_transfer, telebirr, cbe_birr"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Recharge wallet - Organizations only.
    
    Organizations can recharge their wallet to fund bounty programs.
    Minimum recharge: 1000 ETB
    """
    # Only organizations can recharge
    if current_user.role.lower() != UserRole.ORGANIZATION.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organizations can recharge wallet"
        )
    
    # Validate minimum recharge
    if amount < 1000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Minimum recharge amount is 1000 ETB"
        )
    
    # Validate payment method
    valid_methods = ["bank_transfer", "telebirr", "cbe_birr"]
    if payment_method not in valid_methods:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid payment method. Allowed: {', '.join(valid_methods)}"
        )
    
    service = WalletService(db)
    
    try:
        # Generate saga ID for transaction
        from uuid import uuid4
        saga_id = str(uuid4())
        
        # Credit wallet
        result = service.credit_wallet(
            owner_id=current_user.id,
            owner_type="organization",
            amount=Decimal(str(amount)),
            saga_id=saga_id,
            reference_type="wallet_recharge",
            reference_id=None
        )
        
        return {
            "message": "Wallet recharged successfully",
            "transaction_id": result["transaction_id"],
            "amount": amount,
            "payment_method": payment_method,
            "new_balance": result["new_balance"],
            "status": "completed"
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to recharge wallet: {str(e)}"
        )


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
    
    Creates a payout request that requires Finance Officer approval.
    """
    # Only researchers can withdraw
    # ROLE COMPARISON FIX: Compare with enum.value (string) not enum object
    if current_user.role.lower() != UserRole.RESEARCHER.value:
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
    
    # Get researcher profile
    from src.domain.models.researcher import Researcher
    researcher = db.query(Researcher).filter(Researcher.user_id == current_user.id).first()
    if not researcher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Researcher profile not found"
        )
    
    # Check wallet balance
    service = WalletService(db)
    balance_info = service.get_balance(current_user.id, "researcher")
    
    if balance_info["available_balance"] < request.amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient balance. Available: {balance_info['available_balance']} ETB"
        )
    
    try:
        # Create payout request
        from src.domain.models.payment_extended import PayoutRequest
        from datetime import datetime
        from uuid import uuid4
        
        payout_request = PayoutRequest(
            id=uuid4(),
            researcher_id=researcher.id,
            amount=Decimal(str(request.amount)),
            payment_method=request.payment_method,
            payment_details=request.account_details,
            status="pending",
            created_at=datetime.utcnow()
        )
        
        db.add(payout_request)
        db.commit()
        db.refresh(payout_request)
        
        return {
            "message": "Withdrawal request submitted successfully",
            "payout_id": str(payout_request.id),
            "amount": request.amount,
            "payment_method": request.payment_method,
            "status": "pending",
            "note": "Your withdrawal request is pending Finance Officer approval"
        }
    
    except ValueError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        db.rollback()
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
    # CRITICAL FIX: Use current_user.id (user ID), NOT researcher.id or organization.id
    # ROLE COMPARISON FIX: Compare with enum.value (string) not enum object
    if current_user.role.lower() == UserRole.RESEARCHER.value:
        owner_id = current_user.id
        owner_type = "researcher"
    elif current_user.role.lower() == UserRole.ORGANIZATION.value:
        owner_id = current_user.id
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


@router.get("/platform/balance", status_code=status.HTTP_200_OK)
def get_platform_wallet_balance(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get platform wallet balance (Finance Officers only).
    """
    # Only finance officers and admins can view platform wallet
    user_role_lower = current_user.role.lower()
    if user_role_lower not in [UserRole.ADMIN.value, UserRole.SUPER_ADMIN.value, UserRole.FINANCE_OFFICER.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only finance officers and admins can view platform wallet"
        )
    
    service = WalletService(db)
    
    # Platform wallet owner ID
    from uuid import UUID as UUID_TYPE
    platform_owner_id = UUID_TYPE('00000000-0000-0000-0000-000000000000')
    
    balance_info = service.get_balance(platform_owner_id, "platform")
    
    return balance_info


@router.get("/platform/transactions", status_code=status.HTTP_200_OK)
def get_platform_wallet_transactions(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get platform wallet transaction history (Finance Officers only).
    """
    # Only finance officers and admins can view platform wallet
    user_role_lower = current_user.role.lower()
    if user_role_lower not in [UserRole.ADMIN.value, UserRole.SUPER_ADMIN.value, UserRole.FINANCE_OFFICER.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only finance officers and admins can view platform wallet"
        )
    
    service = WalletService(db)
    
    # Platform wallet owner ID
    from uuid import UUID as UUID_TYPE
    platform_owner_id = UUID_TYPE('00000000-0000-0000-0000-000000000000')
    
    transactions = service.get_transaction_history(
        owner_id=platform_owner_id,
        owner_type="platform",
        limit=limit,
        offset=offset
    )
    
    return {
        "transactions": transactions,
        "total": len(transactions),
        "limit": limit,
        "offset": offset
    }


@router.get("/payouts", status_code=status.HTTP_200_OK)
def list_payout_requests(
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List payout requests for finance portal - FREQ-40.
    Finance officers can see all payouts, researchers see only their own.
    """
    from src.domain.models.payment_extended import PayoutRequest
    from src.domain.models.researcher import Researcher
    from sqlalchemy import case
    
    query = db.query(
        PayoutRequest,
        Researcher.username.label('researcher_username'),
        User.email.label('researcher_email')
    ).join(
        Researcher, PayoutRequest.researcher_id == Researcher.id
    ).join(
        User, Researcher.user_id == User.id
    )
    
    # Filter by role
    # ROLE COMPARISON FIX: Compare with enum.value (string) not enum object
    user_role_lower = current_user.role.lower()
    if user_role_lower == UserRole.RESEARCHER.value:
        if not current_user.researcher:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Researcher profile not found"
            )
        query = query.filter(PayoutRequest.researcher_id == current_user.researcher.id)
    elif user_role_lower not in [UserRole.ADMIN.value, UserRole.SUPER_ADMIN.value, UserRole.FINANCE_OFFICER.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Filter by status
    if status:
        query = query.filter(PayoutRequest.status == status)
    
    total = query.count()
    payouts = query.offset(skip).limit(limit).all()
    
    return {
        "payouts": [
            {
                "id": str(p.PayoutRequest.id),
                "researcher_id": str(p.PayoutRequest.researcher_id),
                "researcher_name": p.researcher_username or p.researcher_email or "Unknown",
                "amount": float(p.PayoutRequest.amount),
                "payment_method": p.PayoutRequest.payment_method,
                "status": p.PayoutRequest.status,
                "requested_at": p.PayoutRequest.created_at.isoformat(),
                "processed_at": p.PayoutRequest.processed_at.isoformat() if p.PayoutRequest.processed_at else None,
                "created_at": p.PayoutRequest.created_at.isoformat()
            }
            for p in payouts
        ],
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/payouts/{payout_id}", status_code=status.HTTP_200_OK)
def get_payout_details(
    payout_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get payout request details - FREQ-40.
    """
    from src.domain.models.payment_extended import PayoutRequest
    from uuid import UUID
    
    try:
        payout = db.query(PayoutRequest).filter(
            PayoutRequest.id == UUID(payout_id)
        ).first()
        
        if not payout:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payout request not found"
            )
        
        # Check permissions
        # ROLE COMPARISON FIX: Compare with enum.value (string) not enum object
        user_role_lower = current_user.role.lower()
        if user_role_lower == UserRole.RESEARCHER.value:
            if payout.researcher_id != current_user.researcher.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied"
                )
        elif user_role_lower not in [UserRole.ADMIN.value, UserRole.SUPER_ADMIN.value, UserRole.FINANCE_OFFICER.value]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        return {
            "payout_id": str(payout.id),
            "researcher_id": str(payout.researcher_id),
            "amount": float(payout.amount),
            "payment_method": payout.payment_method,
            "payment_details": payout.payment_details,
            "status": payout.status,
            "failure_reason": payout.failure_reason,
            "created_at": payout.created_at.isoformat(),
            "processed_at": payout.processed_at.isoformat() if payout.processed_at else None
        }
    
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payout ID format"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get payout details: {str(e)}"
        )


@router.post("/payouts/{payout_id}/process", status_code=status.HTTP_200_OK)
def process_payout(
    payout_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Process payout request (Admin/Finance Officer only) - FREQ-40.
    """
    from src.services.payment_service import PaymentService
    from uuid import UUID
    
    # Check permissions
    # ROLE COMPARISON FIX: Compare with enum.value (string) not enum object
    user_role_lower = current_user.role.lower()
    if user_role_lower not in [UserRole.ADMIN.value, UserRole.SUPER_ADMIN.value, UserRole.FINANCE_OFFICER.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only finance officers and admins can process payouts"
        )
    
    try:
        payment_service = PaymentService(db)
        payout = payment_service.process_payout_request(UUID(payout_id))
        
        return {
            "message": "Payout processing started",
            "payout_id": str(payout.id),
            "status": payout.status
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process payout: {str(e)}"
        )


@router.post("/payouts/{payout_id}/approve", status_code=status.HTTP_200_OK)
def approve_payout(
    payout_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Approve payout request (Admin/Finance Officer only) - FREQ-40.
    """
    from src.services.payment_service import PaymentService
    from uuid import UUID
    
    # Check permissions
    # ROLE COMPARISON FIX: Compare with enum.value (string) not enum object
    user_role_lower = current_user.role.lower()
    if user_role_lower not in [UserRole.ADMIN.value, UserRole.SUPER_ADMIN.value, UserRole.FINANCE_OFFICER.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only finance officers and admins can approve payouts"
        )
    
    try:
        payment_service = PaymentService(db)
        payout = payment_service.approve_payout_request(
            payout_id=UUID(payout_id),
            approved_by=current_user.id
        )
        
        return {
            "message": "Payout approved successfully",
            "payout_id": str(payout.id),
            "status": payout.status
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to approve payout: {str(e)}"
        )


@router.post("/payouts/{payout_id}/reject", status_code=status.HTTP_200_OK)
def reject_payout(
    payout_id: str,
    reason: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Reject payout request (Admin/Finance Officer only) - FREQ-40.
    """
    from src.services.payment_service import PaymentService
    from uuid import UUID
    
    # Check permissions
    # ROLE COMPARISON FIX: Compare with enum.value (string) not enum object
    user_role_lower = current_user.role.lower()
    if user_role_lower not in [UserRole.ADMIN.value, UserRole.SUPER_ADMIN.value, UserRole.FINANCE_OFFICER.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only finance officers and admins can reject payouts"
        )
    
    try:
        payment_service = PaymentService(db)
        payout = payment_service.reject_payout_request(
            payout_id=UUID(payout_id),
            rejected_by=current_user.id,
            reason=reason
        )
        
        return {
            "message": "Payout rejected",
            "payout_id": str(payout.id),
            "status": payout.status
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reject payout: {str(e)}"
        )
