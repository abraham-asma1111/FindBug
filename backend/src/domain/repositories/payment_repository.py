"""
Payment Repository — bounty_payments, payout_requests, balances, transactions
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from src.domain.repositories.base import BaseRepository
from src.domain.models.bounty_payment import BountyPayment


class PaymentRepository(BaseRepository[BountyPayment]):
    def __init__(self, db: Session):
        super().__init__(db, BountyPayment)

    def get_by_researcher(self, researcher_id: str, skip: int = 0, limit: int = 20) -> List[BountyPayment]:
        return (
            self.db.query(BountyPayment)
            .filter(BountyPayment.researcher_id == researcher_id)
            .order_by(BountyPayment.created_at.desc())
            .offset(skip).limit(limit).all()
        )

    def get_by_report(self, report_id: str) -> Optional[BountyPayment]:
        return (
            self.db.query(BountyPayment)
            .filter(BountyPayment.report_id == report_id)
            .first()
        )

    def get_pending_payouts(self) -> List[BountyPayment]:
        return (
            self.db.query(BountyPayment)
            .filter(BountyPayment.status == "pending")
            .order_by(BountyPayment.created_at.asc())
            .all()
        )

    def get_by_status(self, status: str, skip: int = 0, limit: int = 20) -> List[BountyPayment]:
        return (
            self.db.query(BountyPayment)
            .filter(BountyPayment.status == status)
            .offset(skip).limit(limit).all()
        )

    def get_total_paid_to_researcher(self, researcher_id: str) -> float:
        from sqlalchemy import func
        result = (
            self.db.query(func.sum(BountyPayment.amount))
            .filter(
                BountyPayment.researcher_id == researcher_id,
                BountyPayment.status == "completed"
            )
            .scalar()
        )
        return float(result or 0.0)

    def approve_payment(self, payment_id: str, approved_by: str) -> Optional[BountyPayment]:
        from datetime import datetime
        payment = self.get_by_id(payment_id)
        if not payment:
            return None
        payment.status = "approved"
        payment.approved_by = approved_by
        payment.approved_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(payment)
        return payment
