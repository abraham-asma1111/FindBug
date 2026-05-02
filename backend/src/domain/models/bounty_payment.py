"""Bounty Payment domain models - FREQ-20 (RAD Table 13)."""
from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import (
    Column, String, DateTime, Numeric, Boolean,
    ForeignKey, func, Index, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSON
from sqlalchemy.orm import relationship

from src.core.database import Base


class BountyPayment(Base):
    """
    Bounty Payment model - FREQ-20, BR-06.
    
    Tracks complete payment transactions with 30% platform commission.
    Organization pays: researcher_amount + commission_amount (30%)
    """
    
    __tablename__ = "bounty_payments"
    
    # Primary identification
    payment_id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    transaction_id = Column(String(100), unique=True, nullable=False)  # Idempotency key
    
    # Relationships
    report_id = Column(PGUUID(as_uuid=True), ForeignKey("vulnerability_reports.id", ondelete="CASCADE"), nullable=False)
    researcher_id = Column(PGUUID(as_uuid=True), ForeignKey("researchers.id"), nullable=False)
    organization_id = Column(PGUUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    
    # Payment amounts (BR-06: 30% commission model)
    researcher_amount = Column(Numeric(15, 2), nullable=False)  # What researcher receives
    commission_amount = Column(Numeric(15, 2), nullable=False)  # 30% platform fee
    total_amount = Column(Numeric(15, 2), nullable=False)  # researcher_amount + commission_amount
    
    # Payment status (State machine: Pending → Approved → Processing → Completed/Failed)
    status = Column(String(50), nullable=False, server_default="pending")
    # Status values: pending, approved, processing, completed, failed, rejected, archived
    
    # Payment method and gateway
    payment_method = Column(String(50), nullable=True)  # telebirr, cbe_birr, bank_transfer, manual
    payment_gateway = Column(String(50), nullable=True)  # telebirr_api, cbe_api, bank_api
    gateway_transaction_id = Column(String(200), nullable=True)  # External transaction ID
    gateway_response = Column(JSON, nullable=True)  # Gateway API response
    
    # Timeline tracking (BR-08: 30-day processing)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    processing_started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    failed_at = Column(DateTime(timezone=True), nullable=True)
    payout_deadline = Column(DateTime(timezone=True), nullable=True)  # approved_at + 30 days
    
    # Approved by
    approved_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Failure handling
    failure_reason = Column(String(500), nullable=True)
    retry_count = Column(Numeric(3, 0), nullable=False, server_default="0")
    
    # KYC verification (BR-08)
    kyc_verified = Column(Boolean, nullable=False, server_default="false")
    kyc_verified_at = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    report = relationship("VulnerabilityReport")
    researcher = relationship("Researcher")
    organization = relationship("Organization")
    approver = relationship("User", foreign_keys=[approved_by])
    history = relationship("PaymentHistory", back_populates="payment", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('ix_bounty_payments_report_id', 'report_id'),
        Index('ix_bounty_payments_researcher_id', 'researcher_id'),
        Index('ix_bounty_payments_organization_id', 'organization_id'),
        Index('ix_bounty_payments_status', 'status'),
        Index('ix_bounty_payments_transaction_id', 'transaction_id'),
        Index('ix_bounty_payments_payout_deadline', 'payout_deadline'),
    )


class Wallet(Base):
    """
    Wallet model for tracking user balances.
    
    Supports organization wallets, researcher wallets, and platform commission wallet.
    """
    
    __tablename__ = "wallets"
    
    wallet_id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Owner (can be organization, researcher, or platform)
    owner_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    owner_type = Column(String(50), nullable=False)  # organization, researcher, platform
    
    # Balance
    balance = Column(Numeric(15, 2), nullable=False, server_default="0.00")
    reserved_balance = Column(Numeric(15, 2), nullable=False, server_default="0.00")  # Funds on hold
    available_balance = Column(Numeric(15, 2), nullable=False, server_default="0.00")  # balance - reserved
    
    # Currency
    currency = Column(String(3), nullable=False, server_default="ETB")  # Ethiopian Birr
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Indexes and constraints
    __table_args__ = (
        Index('ix_wallets_owner_id', 'owner_id'),
        Index('ix_wallets_owner_type', 'owner_type'),
        # Unique constraint to prevent duplicate wallets per owner
        UniqueConstraint('owner_id', 'owner_type', name='uq_wallets_owner_id_owner_type'),
    )


class WalletTransaction(Base):
    """
    Wallet Transaction model for audit trail.
    
    Records all wallet operations (credit, debit, reserve, release).
    """
    
    __tablename__ = "wallet_transactions"
    
    transaction_id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    wallet_id = Column(PGUUID(as_uuid=True), ForeignKey("wallets.wallet_id", ondelete="CASCADE"), nullable=False)
    
    # Transaction details
    transaction_type = Column(String(50), nullable=False)  # credit, debit, reserve, release, compensate
    amount = Column(Numeric(15, 2), nullable=False)
    balance_before = Column(Numeric(15, 2), nullable=False)
    balance_after = Column(Numeric(15, 2), nullable=False)
    
    # Reference
    reference_type = Column(String(50), nullable=True)  # bounty_payment, commission, refund
    reference_id = Column(PGUUID(as_uuid=True), nullable=True)
    
    # Saga pattern
    saga_id = Column(String(100), nullable=True)  # Links related transactions
    compensated = Column(Boolean, nullable=False, server_default="false")
    compensated_at = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    description = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    wallet = relationship("Wallet")
    
    # Indexes
    __table_args__ = (
        Index('ix_wallet_transactions_wallet_id', 'wallet_id'),
        Index('ix_wallet_transactions_saga_id', 'saga_id'),
        Index('ix_wallet_transactions_reference', 'reference_type', 'reference_id'),
    )
