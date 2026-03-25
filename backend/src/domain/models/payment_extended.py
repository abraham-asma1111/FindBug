"""
Extended Payment Models — FREQ-20
payout_requests:  researcher withdrawal requests
transactions:     full financial ledger (all money movements)
payment_gateways: gateway configuration (Telebirr, CBE Birr, bank)
payment_history:  status change audit trail per payment
Aligned with ERD: payout_requests, transactions, payment_gateways, payment_history
"""
import uuid
from datetime import datetime

from sqlalchemy import Column, String, Boolean, DateTime, DECIMAL, Text, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from src.core.database import Base


class PayoutRequest(Base):
    """
    Payout Request — ERD: payout_requests
    Researcher requests to withdraw their available balance.
    """
    __tablename__ = "payout_requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    researcher_id = Column(UUID(as_uuid=True), ForeignKey("researchers.id", ondelete="CASCADE"),
                           nullable=False, index=True)

    amount = Column(DECIMAL(15, 2), nullable=False)
    payment_method = Column(String(50), nullable=False)
    # telebirr | cbe_birr | bank_transfer

    payment_details = Column(JSONB, nullable=True)
    # e.g. {"phone": "...", "account_number": "...", "bank_name": "..."}

    # pending | approved | processing | completed | failed | cancelled
    status = Column(String(20), nullable=False, default="pending", index=True)

    processed_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    processed_at = Column(DateTime, nullable=True)
    failure_reason = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("ix_payout_requests_created_at", "created_at"),
    )

    researcher = relationship("Researcher", back_populates="payout_requests")
    processor = relationship("User", foreign_keys=[processed_by])


class Transaction(Base):
    """
    Transaction — ERD: transactions
    Immutable ledger entry for every money movement on the platform.
    """
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"),
                     nullable=True, index=True)

    # bounty_payment | payout | commission | refund | subscription | adjustment
    type = Column(String(50), nullable=False, index=True)

    amount = Column(DECIMAL(15, 2), nullable=False)

    # pending | completed | failed | reversed
    status = Column(String(20), nullable=False, default="pending", index=True)

    reference_id = Column(UUID(as_uuid=True), nullable=True)  # FK to bounty_payment / payout_request
    reference_type = Column(String(50), nullable=True)        # "bounty_payment" | "payout_request"

    gateway_response = Column(JSONB, nullable=True)  # raw gateway payload

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_transactions_created_at", "created_at"),
        Index("ix_transactions_reference_id", "reference_id"),
    )

    user = relationship("User", back_populates="transactions")


class PaymentGateway(Base):
    """
    Payment Gateway — ERD: payment_gateways
    Configuration record for each active payment gateway.
    """
    __tablename__ = "payment_gateways"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    name = Column(String(100), nullable=False, unique=True)
    # e.g. "Telebirr", "CBE Birr", "Bank Transfer"

    type = Column(String(50), nullable=False)
    # telebirr | cbe_birr | bank_transfer

    config = Column(JSONB, nullable=True)
    # Encrypted gateway credentials / API keys stored here

    is_active = Column(Boolean, nullable=False, default=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)


class PaymentHistory(Base):
    """
    Payment History — ERD: payment_history
    Audit trail of every status change on a bounty_payment record.
    """
    __tablename__ = "payment_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    payment_id = Column(UUID(as_uuid=True), ForeignKey("bounty_payments.payment_id", ondelete="CASCADE"),
                        nullable=False, index=True)

    previous_status = Column(String(20), nullable=False)
    new_status = Column(String(20), nullable=False)
    changed_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    notes = Column(Text, nullable=True)

    changed_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    payment = relationship("BountyPayment", back_populates="history")
    changer = relationship("User", foreign_keys=[changed_by])
