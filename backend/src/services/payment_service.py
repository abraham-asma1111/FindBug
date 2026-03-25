"""
Enhanced Payout Service — Payment processing with KYC verification (FREQ-19, FREQ-20, BR-06, BR-08)
"""
from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import UUID
import uuid

from src.domain.models.bounty_payment import BountyPayment, Wallet, WalletTransaction
from src.domain.models.payment_extended import PayoutRequest, Transaction, PaymentGateway, PaymentHistory
from src.domain.models.kyc import KYCVerification
from src.domain.models.researcher import Researcher
from src.domain.models.organization import Organization
from src.domain.models.report import VulnerabilityReport
from src.core.exceptions import NotFoundException, ForbiddenException, ConflictException
from src.core.logging import get_logger

logger = get_logger(__name__)


class PaymentService:
    """
    Enhanced payment service with KYC verification and comprehensive payout management.
    
    Features:
    - KYC verification before payout
    - Multiple payment gateways (Telebirr, CBE Birr, Bank Transfer)
    - Payout request workflow
    - Transaction ledger
    - Payment history audit trail
    - 30% platform commission (BR-06)
    - 30-day payout deadline (BR-08)
    """
    
    def __init__(self, db: Session):
        self.db = db
        
        # Platform commission rate (BR-06: 30%)
        self.commission_rate = Decimal("0.30")
        
        # Payout deadline (BR-08: 30 days)
        self.payout_deadline_days = 30
        
        # Supported payment methods
        self.payment_methods = ["telebirr", "cbe_birr", "bank_transfer"]
    
    # ═══════════════════════════════════════════════════════════════════════
    # BOUNTY PAYMENT MANAGEMENT
    # ═══════════════════════════════════════════════════════════════════════
    
    def create_bounty_payment(
        self,
        report_id: UUID,
        researcher_amount: Decimal,
        approved_by: UUID
    ) -> BountyPayment:
        """
        Create bounty payment with 30% commission (BR-06).
        
        Args:
            report_id: Report ID
            researcher_amount: Amount for researcher
            approved_by: User ID who approved
            
        Returns:
            BountyPayment
        """
        # Get report
        report = self.db.query(VulnerabilityReport).filter(
            VulnerabilityReport.id == report_id
        ).first()
        
        if not report:
            raise NotFoundException("Report not found")
        
        # Calculate commission (BR-06: 30%)
        commission_amount = researcher_amount * self.commission_rate
        total_amount = researcher_amount + commission_amount
        
        # Generate transaction ID
        transaction_id = f"BP-{uuid.uuid4().hex[:12].upper()}"
        
        # Create payment
        payment = BountyPayment(
            transaction_id=transaction_id,
            report_id=report_id,
            researcher_id=report.researcher_id,
            organization_id=report.program.organization_id,
            researcher_amount=researcher_amount,
            commission_amount=commission_amount,
            total_amount=total_amount,
            status="approved",
            approved_by=approved_by,
            approved_at=datetime.utcnow(),
            payout_deadline=datetime.utcnow() + timedelta(days=self.payout_deadline_days)
        )
        
        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)
        
        # Create payment history
        self._add_payment_history(
            payment_id=payment.payment_id,
            previous_status="pending",
            new_status="approved",
            changed_by=approved_by,
            notes="Bounty payment approved"
        )
        
        # Create transaction record
        self._create_transaction(
            user_id=report.researcher.user_id,
            type="bounty_payment",
            amount=researcher_amount,
            status="pending",
            reference_id=payment.payment_id,
            reference_type="bounty_payment"
        )
        
        logger.info("Bounty payment created", extra={
            "payment_id": str(payment.payment_id),
            "researcher_amount": float(researcher_amount),
            "commission": float(commission_amount),
            "total": float(total_amount)
        })
        
        return payment
    
    def process_bounty_payment(
        self,
        payment_id: UUID,
        payment_method: str,
        payment_gateway: str
    ) -> BountyPayment:
        """
        Process bounty payment through gateway.
        
        Args:
            payment_id: Payment ID
            payment_method: Payment method (telebirr, cbe_birr, bank_transfer)
            payment_gateway: Gateway identifier
            
        Returns:
            Updated BountyPayment
        """
        payment = self.db.query(BountyPayment).filter(
            BountyPayment.payment_id == payment_id
        ).first()
        
        if not payment:
            raise NotFoundException("Payment not found")
        
        if payment.status != "approved":
            raise ValueError(f"Cannot process payment with status: {payment.status}")
        
        # Validate payment method
        if payment_method not in self.payment_methods:
            raise ValueError(f"Invalid payment method. Allowed: {', '.join(self.payment_methods)}")
        
        # Check KYC verification (BR-08)
        if not self._is_kyc_verified(payment.researcher_id):
            raise ForbiddenException("KYC verification required before payout")
        
        # Update payment
        old_status = payment.status
        payment.status = "processing"
        payment.payment_method = payment_method
        payment.payment_gateway = payment_gateway
        payment.processing_started_at = datetime.utcnow()
        payment.kyc_verified = True
        payment.kyc_verified_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(payment)
        
        # Add history
        self._add_payment_history(
            payment_id=payment_id,
            previous_status=old_status,
            new_status="processing",
            changed_by=None,
            notes=f"Payment processing via {payment_method}"
        )
        
        # TODO: Integrate with actual payment gateway API
        # For now, we'll mark as completed immediately
        # In production, this would be async via Celery task
        
        logger.info("Bounty payment processing", extra={
            "payment_id": str(payment_id),
            "method": payment_method
        })
        
        return payment
    
    def complete_bounty_payment(
        self,
        payment_id: UUID,
        gateway_transaction_id: str,
        gateway_response: Optional[Dict] = None
    ) -> BountyPayment:
        """
        Mark bounty payment as completed.
        
        Args:
            payment_id: Payment ID
            gateway_transaction_id: External transaction ID
            gateway_response: Gateway API response
            
        Returns:
            Updated BountyPayment
        """
        payment = self.db.query(BountyPayment).filter(
            BountyPayment.payment_id == payment_id
        ).first()
        
        if not payment:
            raise NotFoundException("Payment not found")
        
        old_status = payment.status
        payment.status = "completed"
        payment.gateway_transaction_id = gateway_transaction_id
        payment.gateway_response = gateway_response
        payment.completed_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(payment)
        
        # Add history
        self._add_payment_history(
            payment_id=payment_id,
            previous_status=old_status,
            new_status="completed",
            changed_by=None,
            notes="Payment completed successfully"
        )
        
        # Update transaction status
        transaction = self.db.query(Transaction).filter(
            Transaction.reference_id == payment_id,
            Transaction.reference_type == "bounty_payment"
        ).first()
        
        if transaction:
            transaction.status = "completed"
            transaction.gateway_response = gateway_response
            self.db.commit()
        
        logger.info("Bounty payment completed", extra={
            "payment_id": str(payment_id),
            "gateway_tx_id": gateway_transaction_id
        })
        
        return payment
    
    # ═══════════════════════════════════════════════════════════════════════
    # PAYOUT REQUEST MANAGEMENT (New - using PayoutRequest model)
    # ═══════════════════════════════════════════════════════════════════════
    
    def create_payout_request(
        self,
        researcher_id: UUID,
        amount: Decimal,
        payment_method: str,
        payment_details: Dict
    ) -> PayoutRequest:
        """
        Create payout request for researcher.
        
        Args:
            researcher_id: Researcher ID
            amount: Payout amount
            payment_method: Payment method (telebirr, cbe_birr, bank_transfer)
            payment_details: Payment details (phone, account_number, etc.)
            
        Returns:
            PayoutRequest
        """
        # Validate researcher
        researcher = self.db.query(Researcher).filter(
            Researcher.id == researcher_id
        ).first()
        
        if not researcher:
            raise NotFoundException("Researcher not found")
        
        # Check KYC verification
        if not self._is_kyc_verified(researcher_id):
            raise ForbiddenException("KYC verification required before payout request")
        
        # Validate payment method
        if payment_method not in self.payment_methods:
            raise ValueError(f"Invalid payment method. Allowed: {', '.join(self.payment_methods)}")
        
        # Validate amount
        if amount <= 0:
            raise ValueError("Amount must be greater than 0")
        
        # TODO: Check available balance in wallet
        # For now, we'll allow the request
        
        # Create payout request
        payout = PayoutRequest(
            researcher_id=researcher_id,
            amount=amount,
            payment_method=payment_method,
            payment_details=payment_details,
            status="pending"
        )
        
        self.db.add(payout)
        self.db.commit()
        self.db.refresh(payout)
        
        logger.info("Payout request created", extra={
            "payout_id": str(payout.id),
            "researcher_id": str(researcher_id),
            "amount": float(amount)
        })
        
        return payout
    
    def approve_payout_request(
        self,
        payout_id: UUID,
        approved_by: UUID
    ) -> PayoutRequest:
        """
        Approve payout request.
        
        Args:
            payout_id: Payout request ID
            approved_by: User ID who approved
            
        Returns:
            Updated PayoutRequest
        """
        payout = self.db.query(PayoutRequest).filter(
            PayoutRequest.id == payout_id
        ).first()
        
        if not payout:
            raise NotFoundException("Payout request not found")
        
        if payout.status != "pending":
            raise ValueError(f"Cannot approve payout with status: {payout.status}")
        
        payout.status = "approved"
        payout.processed_by = approved_by
        payout.processed_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(payout)
        
        logger.info("Payout request approved", extra={
            "payout_id": str(payout_id),
            "approved_by": str(approved_by)
        })
        
        return payout
    
    def process_payout_request(
        self,
        payout_id: UUID
    ) -> PayoutRequest:
        """
        Process approved payout request.
        
        Args:
            payout_id: Payout request ID
            
        Returns:
            Updated PayoutRequest
        """
        payout = self.db.query(PayoutRequest).filter(
            PayoutRequest.id == payout_id
        ).first()
        
        if not payout:
            raise NotFoundException("Payout request not found")
        
        if payout.status != "approved":
            raise ValueError(f"Cannot process payout with status: {payout.status}")
        
        payout.status = "processing"
        self.db.commit()
        self.db.refresh(payout)
        
        # Create transaction record
        self._create_transaction(
            user_id=payout.researcher.user_id,
            type="payout",
            amount=payout.amount,
            status="pending",
            reference_id=payout.id,
            reference_type="payout_request"
        )
        
        # TODO: Integrate with payment gateway
        # For now, mark as completed
        
        logger.info("Payout request processing", extra={
            "payout_id": str(payout_id)
        })
        
        return payout
    
    def complete_payout_request(
        self,
        payout_id: UUID,
        gateway_transaction_id: Optional[str] = None
    ) -> PayoutRequest:
        """
        Mark payout request as completed.
        
        Args:
            payout_id: Payout request ID
            gateway_transaction_id: External transaction ID
            
        Returns:
            Updated PayoutRequest
        """
        payout = self.db.query(PayoutRequest).filter(
            PayoutRequest.id == payout_id
        ).first()
        
        if not payout:
            raise NotFoundException("Payout request not found")
        
        payout.status = "completed"
        self.db.commit()
        self.db.refresh(payout)
        
        # Update transaction
        transaction = self.db.query(Transaction).filter(
            Transaction.reference_id == payout_id,
            Transaction.reference_type == "payout_request"
        ).first()
        
        if transaction:
            transaction.status = "completed"
            self.db.commit()
        
        logger.info("Payout request completed", extra={
            "payout_id": str(payout_id)
        })
        
        return payout
    
    def reject_payout_request(
        self,
        payout_id: UUID,
        rejected_by: UUID,
        reason: str
    ) -> PayoutRequest:
        """
        Reject payout request.
        
        Args:
            payout_id: Payout request ID
            rejected_by: User ID who rejected
            reason: Rejection reason
            
        Returns:
            Updated PayoutRequest
        """
        payout = self.db.query(PayoutRequest).filter(
            PayoutRequest.id == payout_id
        ).first()
        
        if not payout:
            raise NotFoundException("Payout request not found")
        
        payout.status = "failed"
        payout.processed_by = rejected_by
        payout.processed_at = datetime.utcnow()
        payout.failure_reason = reason
        
        self.db.commit()
        self.db.refresh(payout)
        
        logger.info("Payout request rejected", extra={
            "payout_id": str(payout_id),
            "reason": reason
        })
        
        return payout
    
    def list_payout_requests(
        self,
        researcher_id: Optional[UUID] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> List[PayoutRequest]:
        """
        List payout requests.
        
        Args:
            researcher_id: Filter by researcher (optional)
            status: Filter by status (optional)
            skip: Pagination offset
            limit: Maximum results
            
        Returns:
            List of PayoutRequest
        """
        query = self.db.query(PayoutRequest)
        
        if researcher_id:
            query = query.filter(PayoutRequest.researcher_id == researcher_id)
        
        if status:
            query = query.filter(PayoutRequest.status == status)
        
        query = query.order_by(PayoutRequest.created_at.desc())
        
        return query.offset(skip).limit(limit).all()
    
    # ═══════════════════════════════════════════════════════════════════════
    # PAYMENT GATEWAY MANAGEMENT (New - using PaymentGateway model)
    # ═══════════════════════════════════════════════════════════════════════
    
    def configure_payment_gateway(
        self,
        name: str,
        gateway_type: str,
        config: Dict,
        is_active: bool = True
    ) -> PaymentGateway:
        """
        Configure payment gateway.
        
        Args:
            name: Gateway name
            gateway_type: Gateway type (telebirr, cbe_birr, bank_transfer)
            config: Gateway configuration (API keys, credentials)
            is_active: Whether gateway is active
            
        Returns:
            PaymentGateway
        """
        # Check if gateway already exists
        existing = self.db.query(PaymentGateway).filter(
            PaymentGateway.name == name
        ).first()
        
        if existing:
            raise ConflictException(f"Payment gateway '{name}' already exists")
        
        # TODO: Encrypt sensitive config data before storing
        
        gateway = PaymentGateway(
            name=name,
            type=gateway_type,
            config=config,
            is_active=is_active
        )
        
        self.db.add(gateway)
        self.db.commit()
        self.db.refresh(gateway)
        
        logger.info("Payment gateway configured", extra={
            "gateway_id": str(gateway.id),
            "name": name,
            "type": gateway_type
        })
        
        return gateway
    
    def get_active_gateways(self) -> List[PaymentGateway]:
        """
        Get all active payment gateways.
        
        Returns:
            List of active PaymentGateway
        """
        return self.db.query(PaymentGateway).filter(
            PaymentGateway.is_active == True
        ).all()
    
    # ═══════════════════════════════════════════════════════════════════════
    # HELPER METHODS
    # ═══════════════════════════════════════════════════════════════════════
    
    def _is_kyc_verified(self, researcher_id: UUID) -> bool:
        """
        Check if researcher has verified KYC.
        
        Args:
            researcher_id: Researcher ID
            
        Returns:
            True if KYC is verified
        """
        researcher = self.db.query(Researcher).filter(
            Researcher.id == researcher_id
        ).first()
        
        if not researcher:
            return False
        
        kyc = self.db.query(KYCVerification).filter(
            KYCVerification.user_id == researcher.user_id,
            KYCVerification.status == "approved"
        ).first()
        
        return kyc is not None
    
    def _add_payment_history(
        self,
        payment_id: UUID,
        previous_status: str,
        new_status: str,
        changed_by: Optional[UUID],
        notes: Optional[str] = None
    ) -> PaymentHistory:
        """
        Add payment history entry.
        
        Args:
            payment_id: Payment ID
            previous_status: Previous status
            new_status: New status
            changed_by: User who made the change
            notes: Optional notes
            
        Returns:
            PaymentHistory
        """
        history = PaymentHistory(
            payment_id=payment_id,
            previous_status=previous_status,
            new_status=new_status,
            changed_by=changed_by,
            notes=notes
        )
        
        self.db.add(history)
        self.db.commit()
        
        return history
    
    def _create_transaction(
        self,
        user_id: UUID,
        type: str,
        amount: Decimal,
        status: str,
        reference_id: Optional[UUID] = None,
        reference_type: Optional[str] = None,
        gateway_response: Optional[Dict] = None
    ) -> Transaction:
        """
        Create transaction record.
        
        Args:
            user_id: User ID
            type: Transaction type
            amount: Amount
            status: Status
            reference_id: Reference ID
            reference_type: Reference type
            gateway_response: Gateway response
            
        Returns:
            Transaction
        """
        transaction = Transaction(
            user_id=user_id,
            type=type,
            amount=amount,
            status=status,
            reference_id=reference_id,
            reference_type=reference_type,
            gateway_response=gateway_response
        )
        
        self.db.add(transaction)
        self.db.commit()
        
        return transaction
    
    def get_payment_history(self, payment_id: UUID) -> List[PaymentHistory]:
        """
        Get payment history for a bounty payment.
        
        Args:
            payment_id: Payment ID
            
        Returns:
            List of PaymentHistory
        """
        return self.db.query(PaymentHistory).filter(
            PaymentHistory.payment_id == payment_id
        ).order_by(PaymentHistory.changed_at.asc()).all()
    
    def get_transactions(
        self,
        user_id: Optional[UUID] = None,
        type: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[Transaction]:
        """
        Get transactions with filters.
        
        Args:
            user_id: Filter by user
            type: Filter by type
            status: Filter by status
            skip: Pagination offset
            limit: Maximum results
            
        Returns:
            List of Transaction
        """
        query = self.db.query(Transaction)
        
        if user_id:
            query = query.filter(Transaction.user_id == user_id)
        
        if type:
            query = query.filter(Transaction.type == type)
        
        if status:
            query = query.filter(Transaction.status == status)
        
        query = query.order_by(Transaction.created_at.desc())
        
        return query.offset(skip).limit(limit).all()
