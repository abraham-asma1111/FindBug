"""
Payment Endpoints — API routes for payment processing (FREQ-19, FREQ-20, BR-06, BR-08)
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from src.core.database import get_db
from src.core.security import SecurityAudit
from src.services.payment_service import PaymentService
from src.domain.models.user import User
from src.api.v1.middlewares import get_current_user, get_current_verified_user, require_admin
from src.api.v1.schemas.payments import (
    BountyPaymentCreateRequest,
    BountyPaymentResponse,
    BountyPaymentProcessRequest,
    BountyPaymentCompleteRequest,
    PayoutRequestCreate,
    PayoutRequestResponse,
    PayoutApprovalRequest,
    PayoutRejectionRequest,
    PayoutListResponse,
    PaymentGatewayConfigRequest,
    PaymentGatewayResponse,
    TransactionResponse,
    PaymentHistoryResponse
)

router = APIRouter(prefix="/payments", tags=["Payments"])


def get_payment_service(db: Session = Depends(get_db)) -> PaymentService:
    """Dependency to get PaymentService instance"""
    return PaymentService(db)


# ═══════════════════════════════════════════════════════════════════════
# BOUNTY PAYMENT ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════

@router.post(
    "/bounty",
    response_model=BountyPaymentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Bounty Payment",
    description="Create bounty payment with 30% commission (Admin only)"
)
async def create_bounty_payment(
    data: BountyPaymentCreateRequest,
    request: Request,
    current_user: User = Depends(require_admin),
    payment_service: PaymentService = Depends(get_payment_service)
):
    """
    Create bounty payment for approved vulnerability report.
    
    Business Rules:
    - BR-06: 30% platform commission automatically calculated
    - BR-08: 30-day payout deadline set
    - Admin only
    """
    try:
        payment = payment_service.create_bounty_payment(
            report_id=UUID(data.report_id),
            researcher_amount=data.researcher_amount,
            approved_by=current_user.id
        )
        
        # Log security event
        SecurityAudit.log_security_event(
            "BOUNTY_PAYMENT_CREATED",
            str(current_user.id),
            {
                "payment_id": str(payment.payment_id),
                "report_id": data.report_id,
                "amount": float(data.researcher_amount)
            },
            request
        )
        
        return BountyPaymentResponse(
            payment_id=str(payment.payment_id),
            transaction_id=payment.transaction_id,
            report_id=str(payment.report_id),
            researcher_id=str(payment.researcher_id),
            researcher_amount=float(payment.researcher_amount),
            commission_amount=float(payment.commission_amount),
            total_amount=float(payment.total_amount),
            status=payment.status,
            payout_deadline=payment.payout_deadline.isoformat(),
            created_at=payment.created_at.isoformat()
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bounty payment creation failed: {str(e)}"
        )


@router.post(
    "/bounty/{payment_id}/process",
    response_model=BountyPaymentResponse,
    summary="Process Bounty Payment",
    description="Process bounty payment through gateway (Admin only)"
)
async def process_bounty_payment(
    payment_id: str,
    data: BountyPaymentProcessRequest,
    request: Request,
    current_user: User = Depends(require_admin),
    payment_service: PaymentService = Depends(get_payment_service)
):
    """
    Process bounty payment through payment gateway.
    
    Requirements:
    - BR-08: KYC verification required
    - Payment must be in 'approved' status
    - Valid payment method (telebirr, cbe_birr, bank_transfer)
    """
    try:
        payment = payment_service.process_bounty_payment(
            payment_id=UUID(payment_id),
            payment_method=data.payment_method,
            payment_gateway=data.payment_gateway
        )
        
        # Log security event
        SecurityAudit.log_security_event(
            "BOUNTY_PAYMENT_PROCESSING",
            str(current_user.id),
            {
                "payment_id": payment_id,
                "method": data.payment_method
            },
            request
        )
        
        return BountyPaymentResponse(
            payment_id=str(payment.payment_id),
            transaction_id=payment.transaction_id,
            report_id=str(payment.report_id),
            researcher_id=str(payment.researcher_id),
            researcher_amount=float(payment.researcher_amount),
            commission_amount=float(payment.commission_amount),
            total_amount=float(payment.total_amount),
            status=payment.status,
            payment_method=payment.payment_method,
            payment_gateway=payment.payment_gateway,
            payout_deadline=payment.payout_deadline.isoformat(),
            created_at=payment.created_at.isoformat()
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bounty payment processing failed: {str(e)}"
        )


@router.post(
    "/bounty/{payment_id}/complete",
    response_model=BountyPaymentResponse,
    summary="Complete Bounty Payment",
    description="Mark bounty payment as completed (Admin only)"
)
async def complete_bounty_payment(
    payment_id: str,
    data: BountyPaymentCompleteRequest,
    request: Request,
    current_user: User = Depends(require_admin),
    payment_service: PaymentService = Depends(get_payment_service)
):
    """
    Mark bounty payment as completed after gateway confirmation.
    """
    try:
        payment = payment_service.complete_bounty_payment(
            payment_id=UUID(payment_id),
            gateway_transaction_id=data.gateway_transaction_id,
            gateway_response=data.gateway_response
        )
        
        # Log security event
        SecurityAudit.log_security_event(
            "BOUNTY_PAYMENT_COMPLETED",
            str(current_user.id),
            {
                "payment_id": payment_id,
                "gateway_tx_id": data.gateway_transaction_id
            },
            request
        )
        
        return BountyPaymentResponse(
            payment_id=str(payment.payment_id),
            transaction_id=payment.transaction_id,
            report_id=str(payment.report_id),
            researcher_id=str(payment.researcher_id),
            researcher_amount=float(payment.researcher_amount),
            commission_amount=float(payment.commission_amount),
            total_amount=float(payment.total_amount),
            status=payment.status,
            payment_method=payment.payment_method,
            payment_gateway=payment.payment_gateway,
            gateway_transaction_id=payment.gateway_transaction_id,
            payout_deadline=payment.payout_deadline.isoformat(),
            completed_at=payment.completed_at.isoformat() if payment.completed_at else None,
            created_at=payment.created_at.isoformat()
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bounty payment completion failed: {str(e)}"
        )


# ═══════════════════════════════════════════════════════════════════════
# PAYOUT REQUEST ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════

@router.post(
    "/payout/request",
    response_model=PayoutRequestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Payout Request",
    description="Create payout request for researcher"
)
async def create_payout_request(
    data: PayoutRequestCreate,
    request: Request,
    current_user: User = Depends(get_current_verified_user),
    payment_service: PaymentService = Depends(get_payment_service)
):
    """
    Create payout request for researcher.
    
    Requirements:
    - BR-08: KYC verification required
    - Valid payment method (telebirr, cbe_birr, bank_transfer)
    - Amount must be greater than 0
    """
    try:
        # Get researcher ID from user
        from src.domain.models.researcher import Researcher
        researcher = payment_service.db.query(Researcher).filter(
            Researcher.user_id == current_user.id
        ).first()
        
        if not researcher:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only researchers can create payout requests"
            )
        
        payout = payment_service.create_payout_request(
            researcher_id=researcher.id,
            amount=data.amount,
            payment_method=data.payment_method,
            payment_details=data.payment_details
        )
        
        # Log security event
        SecurityAudit.log_security_event(
            "PAYOUT_REQUEST_CREATED",
            str(current_user.id),
            {
                "payout_id": str(payout.id),
                "amount": float(data.amount)
            },
            request
        )
        
        return PayoutRequestResponse(
            payout_id=str(payout.id),
            researcher_id=str(payout.researcher_id),
            amount=float(payout.amount),
            payment_method=payout.payment_method,
            payment_details=payout.payment_details,
            status=payout.status,
            created_at=payout.created_at.isoformat()
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Payout request creation failed: {str(e)}"
        )


@router.get(
    "/payout/my-requests",
    response_model=PayoutListResponse,
    summary="Get My Payout Requests",
    description="Get payout requests for current researcher"
)
async def get_my_payout_requests(
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    payment_service: PaymentService = Depends(get_payment_service)
):
    """
    Get payout requests for current researcher.
    
    Optional filters:
    - status: Filter by status (pending, approved, processing, completed, failed)
    """
    try:
        # Get researcher ID from user
        from src.domain.models.researcher import Researcher
        researcher = payment_service.db.query(Researcher).filter(
            Researcher.user_id == current_user.id
        ).first()
        
        if not researcher:
            return PayoutListResponse(payouts=[], total=0)
        
        payouts = payment_service.list_payout_requests(
            researcher_id=researcher.id,
            status=status,
            skip=skip,
            limit=limit
        )
        
        return PayoutListResponse(
            payouts=[
                PayoutRequestResponse(
                    payout_id=str(p.id),
                    researcher_id=str(p.researcher_id),
                    amount=float(p.amount),
                    payment_method=p.payment_method,
                    payment_details=p.payment_details,
                    status=p.status,
                    created_at=p.created_at.isoformat(),
                    processed_at=p.processed_at.isoformat() if p.processed_at else None
                )
                for p in payouts
            ],
            total=len(payouts)
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get payout requests: {str(e)}"
        )


@router.get(
    "/payout/admin/pending",
    response_model=PayoutListResponse,
    summary="Get Pending Payout Requests",
    description="Get pending payout requests for admin review (Admin only)"
)
async def get_pending_payouts(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(require_admin),
    payment_service: PaymentService = Depends(get_payment_service)
):
    """
    Get pending payout requests (admin only).
    """
    try:
        payouts = payment_service.list_payout_requests(
            status="pending",
            skip=skip,
            limit=limit
        )
        
        return PayoutListResponse(
            payouts=[
                PayoutRequestResponse(
                    payout_id=str(p.id),
                    researcher_id=str(p.researcher_id),
                    amount=float(p.amount),
                    payment_method=p.payment_method,
                    payment_details=p.payment_details,
                    status=p.status,
                    created_at=p.created_at.isoformat()
                )
                for p in payouts
            ],
            total=len(payouts)
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get pending payouts: {str(e)}"
        )


@router.post(
    "/payout/{payout_id}/approve",
    response_model=PayoutRequestResponse,
    summary="Approve Payout Request",
    description="Approve payout request (Admin only)"
)
async def approve_payout_request(
    payout_id: str,
    request: Request,
    current_user: User = Depends(require_admin),
    payment_service: PaymentService = Depends(get_payment_service)
):
    """
    Approve payout request (admin only).
    """
    try:
        payout = payment_service.approve_payout_request(
            payout_id=UUID(payout_id),
            approved_by=current_user.id
        )
        
        # Log security event
        SecurityAudit.log_security_event(
            "PAYOUT_REQUEST_APPROVED",
            str(current_user.id),
            {"payout_id": payout_id},
            request
        )
        
        return PayoutRequestResponse(
            payout_id=str(payout.id),
            researcher_id=str(payout.researcher_id),
            amount=float(payout.amount),
            payment_method=payout.payment_method,
            payment_details=payout.payment_details,
            status=payout.status,
            created_at=payout.created_at.isoformat(),
            processed_at=payout.processed_at.isoformat() if payout.processed_at else None
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Payout approval failed: {str(e)}"
        )


@router.post(
    "/payout/{payout_id}/reject",
    response_model=PayoutRequestResponse,
    summary="Reject Payout Request",
    description="Reject payout request (Admin only)"
)
async def reject_payout_request(
    payout_id: str,
    data: PayoutRejectionRequest,
    request: Request,
    current_user: User = Depends(require_admin),
    payment_service: PaymentService = Depends(get_payment_service)
):
    """
    Reject payout request (admin only).
    """
    try:
        payout = payment_service.reject_payout_request(
            payout_id=UUID(payout_id),
            rejected_by=current_user.id,
            reason=data.reason
        )
        
        # Log security event
        SecurityAudit.log_security_event(
            "PAYOUT_REQUEST_REJECTED",
            str(current_user.id),
            {"payout_id": payout_id, "reason": data.reason},
            request
        )
        
        return PayoutRequestResponse(
            payout_id=str(payout.id),
            researcher_id=str(payout.researcher_id),
            amount=float(payout.amount),
            payment_method=payout.payment_method,
            payment_details=payout.payment_details,
            status=payout.status,
            failure_reason=payout.failure_reason,
            created_at=payout.created_at.isoformat(),
            processed_at=payout.processed_at.isoformat() if payout.processed_at else None
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Payout rejection failed: {str(e)}"
        )


# ═══════════════════════════════════════════════════════════════════════
# PAYMENT GATEWAY ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════

@router.post(
    "/gateway/configure",
    response_model=PaymentGatewayResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Configure Payment Gateway",
    description="Configure payment gateway (Admin only)"
)
async def configure_payment_gateway(
    data: PaymentGatewayConfigRequest,
    request: Request,
    current_user: User = Depends(require_admin),
    payment_service: PaymentService = Depends(get_payment_service)
):
    """
    Configure payment gateway (admin only).
    
    Supported gateways:
    - telebirr
    - cbe_birr
    - bank_transfer
    """
    try:
        gateway = payment_service.configure_payment_gateway(
            name=data.name,
            gateway_type=data.gateway_type,
            config=data.config,
            is_active=data.is_active
        )
        
        # Log security event
        SecurityAudit.log_security_event(
            "PAYMENT_GATEWAY_CONFIGURED",
            str(current_user.id),
            {"gateway_id": str(gateway.id), "name": data.name},
            request
        )
        
        return PaymentGatewayResponse(
            gateway_id=str(gateway.id),
            name=gateway.name,
            gateway_type=gateway.type,
            is_active=gateway.is_active,
            created_at=gateway.created_at.isoformat()
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gateway configuration failed: {str(e)}"
        )


@router.get(
    "/gateway/active",
    response_model=list[PaymentGatewayResponse],
    summary="Get Active Gateways",
    description="Get all active payment gateways"
)
async def get_active_gateways(
    current_user: User = Depends(get_current_user),
    payment_service: PaymentService = Depends(get_payment_service)
):
    """
    Get all active payment gateways.
    """
    try:
        gateways = payment_service.get_active_gateways()
        
        return [
            PaymentGatewayResponse(
                gateway_id=str(g.id),
                name=g.name,
                gateway_type=g.type,
                is_active=g.is_active,
                created_at=g.created_at.isoformat()
            )
            for g in gateways
        ]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get active gateways: {str(e)}"
        )


# ═══════════════════════════════════════════════════════════════════════
# TRANSACTION & HISTORY ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════

@router.get(
    "/transactions",
    response_model=list[TransactionResponse],
    summary="Get Transactions",
    description="Get transaction history"
)
async def get_transactions(
    type: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    payment_service: PaymentService = Depends(get_payment_service)
):
    """
    Get transaction history for current user.
    
    Optional filters:
    - type: Filter by type (bounty_payment, payout, commission, refund, subscription, adjustment)
    - status: Filter by status (pending, completed, failed, reversed)
    """
    try:
        transactions = payment_service.get_transactions(
            user_id=current_user.id,
            type=type,
            status=status,
            skip=skip,
            limit=limit
        )
        
        return [
            TransactionResponse(
                transaction_id=str(t.id),
                user_id=str(t.user_id),
                type=t.type,
                amount=float(t.amount),
                status=t.status,
                reference_id=str(t.reference_id) if t.reference_id else None,
                reference_type=t.reference_type,
                created_at=t.created_at.isoformat()
            )
            for t in transactions
        ]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get transactions: {str(e)}"
        )


@router.get(
    "/history/{payment_id}",
    response_model=list[PaymentHistoryResponse],
    summary="Get Payment History",
    description="Get payment history for a bounty payment (Admin only)"
)
async def get_payment_history(
    payment_id: str,
    current_user: User = Depends(require_admin),
    payment_service: PaymentService = Depends(get_payment_service)
):
    """
    Get payment history for a bounty payment (admin only).
    """
    try:
        history = payment_service.get_payment_history(UUID(payment_id))
        
        return [
            PaymentHistoryResponse(
                history_id=str(h.id),
                payment_id=str(h.payment_id),
                previous_status=h.previous_status,
                new_status=h.new_status,
                changed_by=str(h.changed_by) if h.changed_by else None,
                notes=h.notes,
                changed_at=h.changed_at.isoformat()
            )
            for h in history
        ]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get payment history: {str(e)}"
        )
