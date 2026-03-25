"""
Enhanced Payout Service - FREQ-20 (RAD-Compliant).

Implements:
- 30% commission calculation (BR-06)
- KYC verification enforcement (BR-08)
- 30-day processing timeline (BR-08)
- Saga pattern with compensation
- Duplicate bounty handling (BR-07)
"""
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4
from decimal import Decimal
from datetime import datetime, timedelta
import logging

from sqlalchemy.orm import Session
from sqlalchemy import func

from src.domain.models.bounty_payment import BountyPayment
from src.domain.models.report import VulnerabilityReport
from src.domain.models.researcher import Researcher
from src.domain.models.organization import Organization
from src.domain.models.program import BountyProgram
from src.services.wallet_service import WalletService
from src.services.payment_gateways import TelebirrClient, CBEBirrClient, BankTransferClient

logger = logging.getLogger(__name__)


class EnhancedPayoutService:
    """
    RAD-compliant payout service with commission and Saga pattern.
    """
    
    COMMISSION_RATE = Decimal("0.30")  # 30% platform commission (BR-06)
    PAYOUT_DEADLINE_DAYS = 30  # 30-day processing timeline (BR-08)
    
    def __init__(self, db: Session):
        self.db = db
        self.wallet_service = WalletService(db)
    
    def calculate_commission(self, researcher_amount: Decimal) -> Dict[str, Decimal]:
        """
        Calculate 30% commission (BR-06).
        
        Args:
            researcher_amount: Amount researcher receives
            
        Returns:
            Dict with researcher_amount, commission_amount, total_amount
            
        Example:
            researcher_amount = 1000
            commission_amount = 300 (30%)
            total_amount = 1300 (what organization pays)
        """
        commission_amount = researcher_amount * self.COMMISSION_RATE
        total_amount = researcher_amount + commission_amount
        
        return {
            "researcher_amount": researcher_amount,
            "commission_amount": commission_amount,
            "total_amount": total_amount
        }
    
    def check_kyc_verified(self, researcher_id: UUID) -> bool:
        """
        Check if researcher KYC is verified (BR-08).
        
        Args:
            researcher_id: Researcher ID
            
        Returns:
            True if KYC verified
            
        Raises:
            ValueError: If KYC not verified
        """
        researcher = self.db.query(Researcher).filter(
            Researcher.id == researcher_id
        ).first()
        
        if not researcher:
            raise ValueError("Researcher not found")
        
        if researcher.kyc_status != "verified":
            raise ValueError(
                f"Cannot process payout: KYC status is '{researcher.kyc_status}'. "
                "Researcher must complete KYC verification first."
            )
        
        return True
    
    def calculate_duplicate_bounty(
        self,
        original_amount: Decimal,
        is_duplicate: bool,
        duplicate_detected_at: Optional[datetime],
        original_submitted_at: datetime
    ) -> Decimal:
        """
        Calculate bounty for duplicate reports (BR-07).
        
        Rules:
        - First valid report: 100% bounty
        - Duplicate within 24 hours: 50% bounty
        - Duplicate after 24 hours: 0% bounty
        
        Args:
            original_amount: Original bounty amount
            is_duplicate: Whether report is duplicate
            duplicate_detected_at: When duplicate was detected
            original_submitted_at: When original report was submitted
            
        Returns:
            Adjusted bounty amount
        """
        if not is_duplicate:
            return original_amount
        
        if not duplicate_detected_at:
            return Decimal("0")
        
        # Calculate time difference
        time_diff = duplicate_detected_at - original_submitted_at
        hours_diff = time_diff.total_seconds() / 3600
        
        if hours_diff <= 24:
            # Within 24 hours: 50% bounty
            return original_amount * Decimal("0.50")
        else:
            # After 24 hours: 0% bounty
            return Decimal("0")
    
    def create_bounty_payment(
        self,
        report_id: UUID,
        researcher_amount: Decimal,
        approved_by: UUID
    ) -> BountyPayment:
        """
        Create bounty payment record with commission calculation.
        
        Args:
            report_id: Vulnerability report ID
            researcher_amount: Amount researcher receives
            approved_by: User who approved the payment
            
        Returns:
            BountyPayment instance
            
        Raises:
            ValueError: If validation fails
        """
        # Get report
        report = self.db.query(VulnerabilityReport).filter(
            VulnerabilityReport.id == report_id
        ).first()
        
        if not report:
            raise ValueError("Report not found")
        
        # Check KYC (BR-08)
        self.check_kyc_verified(report.researcher_id)
        
        # Handle duplicate bounty (BR-07)
        if report.is_duplicate:
            researcher_amount = self.calculate_duplicate_bounty(
                researcher_amount,
                report.is_duplicate,
                report.duplicate_detected_at,
                report.submitted_at
            )
            
            if researcher_amount == 0:
                raise ValueError(
                    "Duplicate report submitted after 24 hours. No bounty awarded."
                )
        
        # Calculate commission (BR-06)
        amounts = self.calculate_commission(researcher_amount)
        
        # Get organization
        program = self.db.query(BountyProgram).filter(
            BountyProgram.id == report.program_id
        ).first()
        
        if not program:
            raise ValueError("Program not found")
        
        # Generate transaction ID (idempotency key)
        transaction_id = f"PAY-{uuid4().hex[:12].upper()}"
        
        # Calculate payout deadline (BR-08: 30 days)
        payout_deadline = datetime.utcnow() + timedelta(days=self.PAYOUT_DEADLINE_DAYS)
        
        # Create payment record
        payment = BountyPayment(
            transaction_id=transaction_id,
            report_id=report_id,
            researcher_id=report.researcher_id,
            organization_id=program.organization_id,
            researcher_amount=amounts["researcher_amount"],
            commission_amount=amounts["commission_amount"],
            total_amount=amounts["total_amount"],
            status="approved",
            approved_by=approved_by,
            approved_at=datetime.utcnow(),
            payout_deadline=payout_deadline,
            kyc_verified=True,
            kyc_verified_at=datetime.utcnow()
        )
        
        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)
        
        logger.info(
            f"Created bounty payment {payment.payment_id}: "
            f"researcher={amounts['researcher_amount']}, "
            f"commission={amounts['commission_amount']}, "
            f"total={amounts['total_amount']}"
        )
        
        return payment
    
    def process_payment_saga(
        self,
        payment_id: UUID,
        payment_method: str = "manual",
        payment_details: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Process payment using Saga pattern with compensation.
        
        Saga Steps:
        1. Reserve funds from organization wallet
        2. Credit platform commission
        3. Credit researcher wallet
        4. Update payment status
        5. If any step fails → rollback all previous steps
        
        Args:
            payment_id: BountyPayment ID
            payment_method: telebirr, cbe_birr, bank_transfer, manual
            payment_details: Payment gateway details
            
        Returns:
            Payment result
            
        Raises:
            ValueError: If saga fails
        """
        payment = self.db.query(BountyPayment).filter(
            BountyPayment.payment_id == payment_id
        ).first()
        
        if not payment:
            raise ValueError("Payment not found")
        
        if payment.status != "approved":
            raise ValueError(f"Payment status must be 'approved', got '{payment.status}'")
        
        # Generate saga ID
        saga_id = f"SAGA-{payment.transaction_id}"
        
        logger.info(f"Starting payment saga {saga_id}")
        
        try:
            # Update status to processing
            payment.status = "processing"
            payment.processing_started_at = datetime.utcnow()
            payment.payment_method = payment_method
            self.db.commit()
            
            # Step 1: Reserve funds from organization wallet
            logger.info(f"[{saga_id}] Step 1: Reserve funds from organization")
            try:
                self.wallet_service.reserve_funds(
                    owner_id=payment.organization_id,
                    owner_type="organization",
                    amount=payment.total_amount,
                    saga_id=saga_id,
                    reference_type="bounty_payment",
                    reference_id=payment.payment_id
                )
            except Exception as e:
                logger.error(f"[{saga_id}] Step 1 FAILED: {e}")
                payment.status = "failed"
                payment.failed_at = datetime.utcnow()
                payment.failure_reason = f"Insufficient funds: {str(e)}"
                self.db.commit()
                raise ValueError(f"Payment failed: {str(e)}")
            
            # Step 2: Credit platform commission
            logger.info(f"[{saga_id}] Step 2: Credit platform commission")
            try:
                # Platform wallet (owner_id=None for platform)
                from src.core.config import settings
                platform_wallet_id = UUID("00000000-0000-0000-0000-000000000001")  # Platform wallet
                
                self.wallet_service.credit_wallet(
                    owner_id=platform_wallet_id,
                    owner_type="platform",
                    amount=payment.commission_amount,
                    saga_id=saga_id,
                    reference_type="commission",
                    reference_id=payment.payment_id
                )
            except Exception as e:
                logger.error(f"[{saga_id}] Step 2 FAILED: {e}")
                # Compensate Step 1
                self.wallet_service.release_reserved_funds(
                    owner_id=payment.organization_id,
                    owner_type="organization",
                    amount=payment.total_amount,
                    saga_id=saga_id
                )
                payment.status = "failed"
                payment.failed_at = datetime.utcnow()
                payment.failure_reason = f"Commission processing failed: {str(e)}"
                self.db.commit()
                raise ValueError(f"Payment failed: {str(e)}")
            
            # Step 3: Credit researcher wallet (or process via gateway)
            logger.info(f"[{saga_id}] Step 3: Credit researcher wallet")
            try:
                if payment_method == "manual":
                    # Manual payment: just credit wallet
                    self.wallet_service.credit_wallet(
                        owner_id=payment.researcher_id,
                        owner_type="researcher",
                        amount=payment.researcher_amount,
                        saga_id=saga_id,
                        reference_type="bounty_payment",
                        reference_id=payment.payment_id
                    )
                else:
                    # Process via payment gateway
                    gateway_result = self._process_via_gateway(
                        payment,
                        payment_method,
                        payment_details
                    )
                    payment.gateway_transaction_id = gateway_result.get("transaction_id")
                    payment.gateway_response = gateway_result
            except Exception as e:
                logger.error(f"[{saga_id}] Step 3 FAILED: {e}")
                # Compensate Step 2
                self.wallet_service.compensate_credit(
                    owner_id=platform_wallet_id,
                    owner_type="platform",
                    amount=payment.commission_amount,
                    saga_id=saga_id
                )
                # Compensate Step 1
                self.wallet_service.release_reserved_funds(
                    owner_id=payment.organization_id,
                    owner_type="organization",
                    amount=payment.total_amount,
                    saga_id=saga_id
                )
                payment.status = "failed"
                payment.failed_at = datetime.utcnow()
                payment.failure_reason = f"Researcher payout failed: {str(e)}"
                self.db.commit()
                raise ValueError(f"Payment failed: {str(e)}")
            
            # Step 4: Debit organization wallet (complete reservation)
            logger.info(f"[{saga_id}] Step 4: Debit organization wallet")
            try:
                self.wallet_service.debit_wallet(
                    owner_id=payment.organization_id,
                    owner_type="organization",
                    amount=payment.total_amount,
                    saga_id=saga_id,
                    from_reserved=True,
                    reference_type="bounty_payment",
                    reference_id=payment.payment_id
                )
            except Exception as e:
                logger.error(f"[{saga_id}] Step 4 FAILED: {e}")
                # Full rollback
                self.wallet_service.compensate_credit(
                    owner_id=payment.researcher_id,
                    owner_type="researcher",
                    amount=payment.researcher_amount,
                    saga_id=saga_id
                )
                self.wallet_service.compensate_credit(
                    owner_id=platform_wallet_id,
                    owner_type="platform",
                    amount=payment.commission_amount,
                    saga_id=saga_id
                )
                self.wallet_service.release_reserved_funds(
                    owner_id=payment.organization_id,
                    owner_type="organization",
                    amount=payment.total_amount,
                    saga_id=saga_id
                )
                payment.status = "failed"
                payment.failed_at = datetime.utcnow()
                payment.failure_reason = f"Organization debit failed: {str(e)}"
                self.db.commit()
                raise ValueError(f"Payment failed: {str(e)}")
            
            # Success! Update payment status
            payment.status = "completed"
            payment.completed_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"[{saga_id}] Payment saga completed successfully")
            
            return {
                "success": True,
                "payment_id": str(payment.payment_id),
                "transaction_id": payment.transaction_id,
                "researcher_amount": float(payment.researcher_amount),
                "commission_amount": float(payment.commission_amount),
                "total_amount": float(payment.total_amount),
                "status": payment.status,
                "completed_at": payment.completed_at
            }
            
        except Exception as e:
            logger.error(f"[{saga_id}] Saga failed: {e}")
            raise
    
    def _process_via_gateway(
        self,
        payment: BountyPayment,
        payment_method: str,
        payment_details: Optional[Dict]
    ) -> Dict[str, Any]:
        """
        Process payment via payment gateway.
        
        Args:
            payment: BountyPayment instance
            payment_method: telebirr, cbe_birr, bank_transfer
            payment_details: Gateway-specific details
            
        Returns:
            Gateway response
        """
        # TODO: Get gateway credentials from config
        if payment_method == "telebirr":
            client = TelebirrClient(
                api_key="YOUR_TELEBIRR_API_KEY",
                merchant_id="YOUR_MERCHANT_ID"
            )
            return client.initiate_payment(
                amount=payment.researcher_amount,
                phone_number=payment_details.get("phone_number"),
                reference_id=payment.transaction_id,
                description=f"Bug bounty payment for report {payment.report_id}"
            )
        
        elif payment_method == "cbe_birr":
            client = CBEBirrClient(
                api_key="YOUR_CBE_API_KEY",
                merchant_code="YOUR_MERCHANT_CODE"
            )
            return client.initiate_payment(
                amount=payment.researcher_amount,
                phone_number=payment_details.get("phone_number"),
                reference_id=payment.transaction_id
            )
        
        elif payment_method == "bank_transfer":
            client = BankTransferClient(
                api_key="YOUR_BANK_API_KEY",
                bank_code=payment_details.get("bank_code", "CBE")
            )
            return client.initiate_transfer(
                amount=payment.researcher_amount,
                account_number=payment_details.get("account_number"),
                account_name=payment_details.get("account_name"),
                bank_code=payment_details.get("bank_code"),
                reference_id=payment.transaction_id
            )
        
        else:
            raise ValueError(f"Unsupported payment method: {payment_method}")
    
    def get_overdue_payments(self) -> list:
        """
        Get payments that are overdue (past 30-day deadline).
        
        Returns:
            List of overdue payments
        """
        now = datetime.utcnow()
        
        overdue = self.db.query(BountyPayment).filter(
            BountyPayment.status.in_(["approved", "processing"]),
            BountyPayment.payout_deadline < now
        ).all()
        
        return [
            {
                "payment_id": str(p.payment_id),
                "transaction_id": p.transaction_id,
                "researcher_id": str(p.researcher_id),
                "amount": float(p.researcher_amount),
                "approved_at": p.approved_at,
                "deadline": p.payout_deadline,
                "days_overdue": (now - p.payout_deadline).days
            }
            for p in overdue
        ]
