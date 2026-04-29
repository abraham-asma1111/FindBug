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
from src.core.dependencies import get_current_user, get_current_verified_user, require_admin, require_financial
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
# PAYMENT LIST & APPROVAL ENDPOINTS (Finance Portal)
# ═══════════════════════════════════════════════════════════════════════

@router.get(
    "/history",
    summary="List Payment History",
    description="List all bounty payments with filters (Finance Officer/Admin only)"
)
async def list_payment_history(
    status: Optional[str] = None,
    researcher_id: Optional[str] = None,
    organization_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(require_financial),
    payment_service: PaymentService = Depends(get_payment_service),
    db: Session = Depends(get_db)
):
    """
    List all bounty payments with enriched data (Finance Officer/Admin only).
    
    Returns payments with researcher, organization, and report details.
    """
    from src.domain.models.researcher import Researcher
    from src.domain.models.organization import Organization
    from src.domain.models.report import VulnerabilityReport
    
    try:
        # Convert string IDs to UUID if provided
        researcher_uuid = UUID(researcher_id) if researcher_id else None
        organization_uuid = UUID(organization_id) if organization_id else None
        
        payments, total = payment_service.list_bounty_payments(
            status=status,
            researcher_id=researcher_uuid,
            organization_id=organization_uuid,
            skip=skip,
            limit=limit
        )
        
        # Enrich with related data
        enriched_payments = []
        for payment in payments:
            # Get researcher
            researcher = db.query(Researcher).filter(Researcher.id == payment.researcher_id).first()
            # Get organization
            organization = db.query(Organization).filter(Organization.id == payment.organization_id).first()
            # Get report
            report = db.query(VulnerabilityReport).filter(VulnerabilityReport.id == payment.report_id).first()
            
            enriched_payments.append({
                "payment_id": str(payment.payment_id),
                "transaction_id": payment.transaction_id,
                "report_id": str(payment.report_id),
                "report_title": report.title if report else None,
                "report_severity": report.severity if report else None,
                "researcher_id": str(payment.researcher_id),
                "researcher_name": researcher.username if researcher else "Unknown",
                "organization_id": str(payment.organization_id),
                "organization_name": organization.company_name if organization else "Unknown",
                "researcher_amount": float(payment.researcher_amount),
                "commission_amount": float(payment.commission_amount),
                "total_amount": float(payment.total_amount),
                "status": payment.status,
                "payment_method": payment.payment_method,
                "kyc_verified": payment.kyc_verified,
                "approved_at": payment.approved_at.isoformat() if payment.approved_at else None,
                "payout_deadline": payment.payout_deadline.isoformat() if payment.payout_deadline else None,
                "created_at": payment.created_at.isoformat(),
                "failure_reason": payment.failure_reason
            })
        
        return {
            "payments": enriched_payments,
            "total": total,
            "skip": skip,
            "limit": limit
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list payments: {str(e)}"
        )


@router.post(
    "/{payment_id}/approve",
    summary="Approve Payment",
    description="Approve bounty payment and credit researcher wallet (Finance Officer/Admin only)"
)
async def approve_payment(
    payment_id: str,
    request: Request,
    current_user: User = Depends(require_financial),
    payment_service: PaymentService = Depends(get_payment_service)
):
    """
    Approve bounty payment (Finance Officer/Admin only).
    
    This action:
    1. Verifies KYC
    2. Approves payment
    3. Credits researcher wallet
    4. Sets payout deadline (30 days)
    """
    try:
        payment = payment_service.approve_bounty_payment(
            payment_id=UUID(payment_id),
            approved_by=current_user.id
        )
        
        # Log security event
        SecurityAudit.log_security_event(
            "PAYMENT_APPROVED",
            str(current_user.id),
            {
                "payment_id": payment_id,
                "amount": float(payment.researcher_amount)
            },
            request
        )
        
        return {
            "message": "Payment approved and wallet credited successfully",
            "payment_id": str(payment.payment_id),
            "status": payment.status,
            "researcher_amount": float(payment.researcher_amount),
            "payout_deadline": payment.payout_deadline.isoformat() if payment.payout_deadline else None
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Payment approval failed: {str(e)}"
        )


@router.post(
    "/{payment_id}/reject",
    summary="Reject Payment",
    description="Reject bounty payment (Finance Officer/Admin only)"
)
async def reject_payment(
    payment_id: str,
    reason: str,
    request: Request,
    current_user: User = Depends(require_financial),
    payment_service: PaymentService = Depends(get_payment_service)
):
    """
    Reject bounty payment (Finance Officer/Admin only).
    """
    try:
        payment = payment_service.reject_bounty_payment(
            payment_id=UUID(payment_id),
            rejected_by=current_user.id,
            reason=reason
        )
        
        # Log security event
        SecurityAudit.log_security_event(
            "PAYMENT_REJECTED",
            str(current_user.id),
            {
                "payment_id": payment_id,
                "reason": reason
            },
            request
        )
        
        return {
            "message": "Payment rejected",
            "payment_id": str(payment.payment_id),
            "status": payment.status,
            "failure_reason": payment.failure_reason
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Payment rejection failed: {str(e)}"
        )


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
# PAYMENT METHODS ENDPOINT
# ═══════════════════════════════════════════════════════════════════════

@router.get(
    "/methods",
    summary="Get Payment Methods",
    description="Get available payment methods"
)
async def get_payment_methods(
    current_user: User = Depends(get_current_user)
):
    """
    Get available payment methods.
    
    Returns list of supported payment methods:
    - telebirr
    - cbe_birr
    - bank_transfer
    """
    return {
        "payment_methods": [
            {
                "id": "telebirr",
                "name": "TeleBirr",
                "type": "mobile_money",
                "description": "Mobile money payment via TeleBirr",
                "is_active": True
            },
            {
                "id": "cbe_birr",
                "name": "CBE Birr",
                "type": "mobile_money",
                "description": "Mobile money payment via CBE Birr",
                "is_active": True
            },
            {
                "id": "bank_transfer",
                "name": "Bank Transfer",
                "type": "bank",
                "description": "Direct bank transfer",
                "is_active": True
            }
        ]
    }


# ═══════════════════════════════════════════════════════════════════════
# PAYOUTS LIST ENDPOINT
# ═══════════════════════════════════════════════════════════════════════

@router.get(
    "/payouts",
    response_model=PayoutListResponse,
    summary="Get Payouts",
    description="Get payout requests (alias for /payout/my-requests)"
)
async def get_payouts(
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    payment_service: PaymentService = Depends(get_payment_service)
):
    """
    Get payout requests for current user.
    
    This is an alias for /payout/my-requests for convenience.
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
            detail=f"Failed to get payouts: {str(e)}"
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


@router.get(
    "/analytics",
    summary="Get Payment Analytics",
    description="Get payment analytics and trends (Finance Officer/Admin only)"
)
async def get_payment_analytics(
    range: str = "30d",
    current_user: User = Depends(require_admin),
    payment_service: PaymentService = Depends(get_payment_service)
):
    """
    Get payment analytics and trends (finance officer/admin only).
    
    Range options: 7d, 30d, 90d, 1y
    """
    try:
        from datetime import datetime, timedelta
        from sqlalchemy import func
        from src.domain.models.bounty_payment import BountyPayment
        from src.domain.models.researcher import Researcher
        from src.domain.models.organization import Organization
        from src.domain.models.report import VulnerabilityReport
        
        # Calculate date range
        range_days = {
            '7d': 7,
            '30d': 30,
            '90d': 90,
            '1y': 365
        }.get(range, 30)
        
        start_date = datetime.utcnow() - timedelta(days=range_days)
        
        # Get stats
        payments = payment_service.db.query(BountyPayment).filter(
            BountyPayment.created_at >= start_date
        ).all()
        
        total_payments = len(payments)
        total_amount = sum(float(p.researcher_amount) for p in payments)
        total_commission = sum(float(p.commission_amount) for p in payments)
        avg_payment = total_amount / total_payments if total_payments > 0 else 0
        
        # Payment trends (daily aggregation)
        trends = payment_service.db.query(
            func.date(BountyPayment.created_at).label('date'),
            func.sum(BountyPayment.researcher_amount).label('amount'),
            func.sum(BountyPayment.commission_amount).label('commission')
        ).filter(
            BountyPayment.created_at >= start_date
        ).group_by(
            func.date(BountyPayment.created_at)
        ).all()
        
        payment_trends = [
            {
                'date': str(t.date),
                'amount': float(t.amount or 0),
                'commission': float(t.commission or 0)
            }
            for t in trends
        ]
        
        # Severity distribution
        severity_dist = {}
        for p in payments:
            # Get report severity
            report = payment_service.db.query(VulnerabilityReport).filter(VulnerabilityReport.id == p.report_id).first()
            if report:
                severity = report.severity or 'unknown'
                severity_dist[severity] = severity_dist.get(severity, 0) + float(p.researcher_amount)
        
        severity_distribution = [
            {'name': k.capitalize(), 'value': v}
            for k, v in severity_dist.items()
        ]
        
        # Monthly comparison
        monthly = payment_service.db.query(
            func.date_trunc('month', BountyPayment.created_at).label('month'),
            func.sum(BountyPayment.researcher_amount).label('amount'),
            func.count(BountyPayment.payment_id).label('count')
        ).filter(
            BountyPayment.created_at >= start_date
        ).group_by(
            func.date_trunc('month', BountyPayment.created_at)
        ).all()
        
        monthly_comparison = [
            {
                'month': str(m.month)[:7],  # YYYY-MM format
                'amount': float(m.amount or 0),
                'count': int(m.count or 0)
            }
            for m in monthly
        ]
        
        # Top researchers
        top_researchers = payment_service.db.query(
            Researcher.id,
            Researcher.username,
            func.count(BountyPayment.payment_id).label('report_count'),
            func.sum(BountyPayment.researcher_amount).label('total_earned'),
            func.avg(BountyPayment.researcher_amount).label('avg_payment')
        ).join(
            BountyPayment, BountyPayment.researcher_id == Researcher.id
        ).filter(
            BountyPayment.created_at >= start_date
        ).group_by(
            Researcher.id, Researcher.username
        ).order_by(
            func.sum(BountyPayment.researcher_amount).desc()
        ).limit(10).all()
        
        # Top organizations
        top_organizations = payment_service.db.query(
            Organization.id,
            Organization.name,
            func.count(BountyPayment.payment_id).label('report_count'),
            func.sum(BountyPayment.total_amount).label('total_spent'),
            func.sum(BountyPayment.commission_amount).label('total_commission')
        ).join(
            VulnerabilityReport, VulnerabilityReport.organization_id == Organization.id
        ).join(
            BountyPayment, BountyPayment.report_id == VulnerabilityReport.id
        ).filter(
            BountyPayment.created_at >= start_date
        ).group_by(
            Organization.id, Organization.name
        ).order_by(
            func.sum(BountyPayment.total_amount).desc()
        ).limit(10).all()
        
        return {
            'stats': {
                'total_payments': total_payments,
                'total_amount': total_amount,
                'avg_payment': avg_payment,
                'total_commission': total_commission
            },
            'payment_trends': payment_trends,
            'severity_distribution': severity_distribution,
            'monthly_comparison': monthly_comparison,
            'top_researchers': [
                {
                    'id': str(r.id),
                    'name': r.username,
                    'report_count': r.report_count,
                    'total_earned': float(r.total_earned or 0),
                    'avg_payment': float(r.avg_payment or 0)
                }
                for r in top_researchers
            ],
            'top_organizations': [
                {
                    'id': str(o.id),
                    'name': o.name,
                    'report_count': o.report_count,
                    'total_spent': float(o.total_spent or 0),
                    'total_commission': float(o.total_commission or 0)
                }
                for o in top_organizations
            ]
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get payment analytics: {str(e)}"
        )


# ═══════════════════════════════════════════════════════════════════════
# PAYMENT DETAIL ENDPOINT
# ═══════════════════════════════════════════════════════════════════════

@router.get(
    "/bounty/{payment_id}",
    response_model=BountyPaymentResponse,
    summary="Get Payment Details",
    description="Get detailed payment information (Admin only)"
)
async def get_payment_details(
    payment_id: str,
    current_user: User = Depends(require_admin),
    payment_service: PaymentService = Depends(get_payment_service)
):
    """Get detailed payment information."""
    try:
        payment = payment_service.db.query(BountyPayment).filter(
            BountyPayment.payment_id == UUID(payment_id)
        ).first()
        
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
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
            payout_deadline=payment.payout_deadline.isoformat() if payment.payout_deadline else None,
            created_at=payment.created_at.isoformat(),
            approved_at=payment.approved_at.isoformat() if payment.approved_at else None,
            completed_at=payment.completed_at.isoformat() if payment.completed_at else None
        )
    
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payment ID format"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get payment details: {str(e)}"
        )


# ═══════════════════════════════════════════════════════════════════════
# FINANCE PORTAL ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════

@router.get(
    "/history",
    summary="List All Payments for Finance Portal",
    description="Get paginated list of all bounty payments (Finance Officer only)"
)
async def list_payments_for_finance(
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_admin),
    payment_service: PaymentService = Depends(get_payment_service),
    db: Session = Depends(get_db)
):
    """
    List all bounty payments for finance portal with filters.
    Returns enriched data with researcher, organization, and report info.
    """
    try:
        from src.domain.models.bounty_payment import BountyPayment
        from src.domain.models.researcher import Researcher
        from src.domain.models.organization import Organization
        from src.domain.models.report import VulnerabilityReport
        
        query = db.query(
            BountyPayment,
            Researcher.username.label('researcher_name'),
            Organization.name.label('organization_name'),
            VulnerabilityReport.title.label('report_title'),
            VulnerabilityReport.severity.label('severity')
        ).join(
            Researcher, BountyPayment.researcher_id == Researcher.id
        ).join(
            Organization, BountyPayment.organization_id == Organization.id
        ).join(
            VulnerabilityReport, BountyPayment.report_id == VulnerabilityReport.id
        )
        
        if status:
            query = query.filter(BountyPayment.status == status)
        
        total = query.count()
        payments = query.offset(skip).limit(limit).all()
        
        return {
            'payments': [
                {
                    'id': str(p.BountyPayment.payment_id),
                    'payment_id': str(p.BountyPayment.payment_id),
                    'transaction_id': p.BountyPayment.transaction_id,
                    'report_id': str(p.BountyPayment.report_id),
                    'researcher_id': str(p.BountyPayment.researcher_id),
                    'researcher_name': p.researcher_name,
                    'organization_name': p.organization_name,
                    'report_title': p.report_title,
                    'severity': p.severity,
                    'researcher_amount': float(p.BountyPayment.researcher_amount),
                    'commission_amount': float(p.BountyPayment.commission_amount),
                    'total_amount': float(p.BountyPayment.total_amount),
                    'status': p.BountyPayment.status,
                    'payment_method': p.BountyPayment.payment_method,
                    'created_at': p.BountyPayment.created_at.isoformat(),
                    'completed_at': p.BountyPayment.completed_at.isoformat() if p.BountyPayment.completed_at else None,
                    'payout_deadline': p.BountyPayment.payout_deadline.isoformat() if p.BountyPayment.payout_deadline else None
                }
                for p in payments
            ],
            'total': total,
            'skip': skip,
            'limit': limit
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch payments: {str(e)}"
        )


@router.post(
    "/{payment_id}/approve",
    summary="Approve Payment",
    description="Approve a pending bounty payment (Finance Officer only)"
)
async def approve_payment(
    payment_id: str,
    request: Request,
    current_user: User = Depends(require_admin),
    payment_service: PaymentService = Depends(get_payment_service)
):
    """Approve a pending bounty payment."""
    try:
        from src.domain.models.bounty_payment import BountyPayment
        
        payment = payment_service.db.query(BountyPayment).filter(
            BountyPayment.payment_id == UUID(payment_id)
        ).first()
        
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )
        
        if payment.status != 'pending':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot approve payment with status: {payment.status}"
            )
        
        payment.status = 'approved'
        payment.approved_by = current_user.id
        payment_service.db.commit()
        
        # Log security event
        SecurityAudit.log_security_event(
            "PAYMENT_APPROVED",
            str(current_user.id),
            {"payment_id": payment_id},
            request
        )
        
        return {
            'message': 'Payment approved successfully',
            'payment_id': payment_id,
            'status': 'approved'
        }
    
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payment ID format"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to approve payment: {str(e)}"
        )


@router.post(
    "/{payment_id}/reject",
    summary="Reject Payment",
    description="Reject a pending bounty payment (Finance Officer only)"
)
async def reject_payment(
    payment_id: str,
    reason: str,
    request: Request,
    current_user: User = Depends(require_admin),
    payment_service: PaymentService = Depends(get_payment_service)
):
    """Reject a pending bounty payment."""
    try:
        from src.domain.models.bounty_payment import BountyPayment
        
        payment = payment_service.db.query(BountyPayment).filter(
            BountyPayment.payment_id == UUID(payment_id)
        ).first()
        
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )
        
        if payment.status != 'pending':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot reject payment with status: {payment.status}"
            )
        
        payment.status = 'rejected'
        payment.rejection_reason = reason
        payment_service.db.commit()
        
        # Log security event
        SecurityAudit.log_security_event(
            "PAYMENT_REJECTED",
            str(current_user.id),
            {"payment_id": payment_id, "reason": reason},
            request
        )
        
        return {
            'message': 'Payment rejected successfully',
            'payment_id': payment_id,
            'status': 'rejected',
            'reason': reason
        }
    
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payment ID format"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reject payment: {str(e)}"
        )
