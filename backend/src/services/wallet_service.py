"""
Wallet Service - FREQ-20 (RAD Saga Pattern).

Manages wallet balances and transactions with compensation logic.
"""
from typing import Optional, Dict, Any
from uuid import UUID, uuid4
from decimal import Decimal
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import func

from src.domain.models.bounty_payment import Wallet, WalletTransaction


class WalletService:
    """
    Wallet service for balance management.
    
    Implements Saga pattern with compensation for distributed transactions.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_or_create_wallet(
        self,
        owner_id: UUID,
        owner_type: str,
        currency: str = "ETB"
    ) -> Wallet:
        """
        Get existing wallet or create new one.
        
        Args:
            owner_id: User/organization ID
            owner_type: organization, researcher, platform
            currency: Currency code (default: ETB)
            
        Returns:
            Wallet instance
        """
        wallet = self.db.query(Wallet).filter(
            Wallet.owner_id == owner_id,
            Wallet.owner_type == owner_type
        ).first()
        
        if not wallet:
            wallet = Wallet(
                owner_id=owner_id,
                owner_type=owner_type,
                currency=currency
            )
            self.db.add(wallet)
            self.db.commit()
            self.db.refresh(wallet)
        
        return wallet
    
    def reserve_funds(
        self,
        owner_id: UUID,
        owner_type: str,
        amount: Decimal,
        saga_id: str,
        reference_type: str = "bounty_payment",
        reference_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Reserve funds from wallet (Step 1 of Saga).
        
        Args:
            owner_id: Wallet owner ID
            owner_type: organization, researcher, platform
            amount: Amount to reserve
            saga_id: Saga transaction ID for compensation
            reference_type: Transaction reference type
            reference_id: Transaction reference ID
            
        Returns:
            Transaction result
            
        Raises:
            ValueError: If insufficient funds
        """
        wallet = self.get_or_create_wallet(owner_id, owner_type)
        
        # Check available balance
        if wallet.available_balance < amount:
            raise ValueError(
                f"Insufficient funds: available={wallet.available_balance}, required={amount}"
            )
        
        # Reserve funds
        balance_before = wallet.balance
        wallet.reserved_balance += amount
        wallet.available_balance = wallet.balance - wallet.reserved_balance
        
        # Record transaction
        transaction = WalletTransaction(
            wallet_id=wallet.wallet_id,
            transaction_type="reserve",
            amount=amount,
            balance_before=balance_before,
            balance_after=wallet.balance,
            reference_type=reference_type,
            reference_id=reference_id,
            saga_id=saga_id,
            description=f"Reserved {amount} {wallet.currency} for {reference_type}"
        )
        
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(wallet)
        
        return {
            "success": True,
            "wallet_id": str(wallet.wallet_id),
            "transaction_id": str(transaction.transaction_id),
            "reserved_amount": float(amount),
            "available_balance": float(wallet.available_balance)
        }
    
    def credit_wallet(
        self,
        owner_id: UUID,
        owner_type: str,
        amount: Decimal,
        saga_id: str,
        reference_type: str = "bounty_payment",
        reference_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Credit wallet (add funds).
        
        Args:
            owner_id: Wallet owner ID
            owner_type: organization, researcher, platform
            amount: Amount to credit
            saga_id: Saga transaction ID
            reference_type: Transaction reference type
            reference_id: Transaction reference ID
            
        Returns:
            Transaction result
        """
        wallet = self.get_or_create_wallet(owner_id, owner_type)
        
        balance_before = wallet.balance
        wallet.balance += amount
        wallet.available_balance = wallet.balance - wallet.reserved_balance
        
        # Record transaction
        transaction = WalletTransaction(
            wallet_id=wallet.wallet_id,
            transaction_type="credit",
            amount=amount,
            balance_before=balance_before,
            balance_after=wallet.balance,
            reference_type=reference_type,
            reference_id=reference_id,
            saga_id=saga_id,
            description=f"Credited {amount} {wallet.currency} from {reference_type}"
        )
        
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(wallet)
        
        return {
            "success": True,
            "wallet_id": str(wallet.wallet_id),
            "transaction_id": str(transaction.transaction_id),
            "credited_amount": float(amount),
            "new_balance": float(wallet.balance)
        }
    
    def debit_wallet(
        self,
        owner_id: UUID,
        owner_type: str,
        amount: Decimal,
        saga_id: str,
        from_reserved: bool = True,
        reference_type: str = "bounty_payment",
        reference_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Debit wallet (remove funds).
        
        Args:
            owner_id: Wallet owner ID
            owner_type: organization, researcher, platform
            amount: Amount to debit
            saga_id: Saga transaction ID
            from_reserved: Debit from reserved balance
            reference_type: Transaction reference type
            reference_id: Transaction reference ID
            
        Returns:
            Transaction result
            
        Raises:
            ValueError: If insufficient funds
        """
        wallet = self.get_or_create_wallet(owner_id, owner_type)
        
        if from_reserved:
            if wallet.reserved_balance < amount:
                raise ValueError(f"Insufficient reserved funds: {wallet.reserved_balance}")
            
            balance_before = wallet.balance
            wallet.balance -= amount
            wallet.reserved_balance -= amount
            wallet.available_balance = wallet.balance - wallet.reserved_balance
        else:
            if wallet.available_balance < amount:
                raise ValueError(f"Insufficient available funds: {wallet.available_balance}")
            
            balance_before = wallet.balance
            wallet.balance -= amount
            wallet.available_balance = wallet.balance - wallet.reserved_balance
        
        # Record transaction
        transaction = WalletTransaction(
            wallet_id=wallet.wallet_id,
            transaction_type="debit",
            amount=amount,
            balance_before=balance_before,
            balance_after=wallet.balance,
            reference_type=reference_type,
            reference_id=reference_id,
            saga_id=saga_id,
            description=f"Debited {amount} {wallet.currency} for {reference_type}"
        )
        
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(wallet)
        
        return {
            "success": True,
            "wallet_id": str(wallet.wallet_id),
            "transaction_id": str(transaction.transaction_id),
            "debited_amount": float(amount),
            "new_balance": float(wallet.balance)
        }
    
    def release_reserved_funds(
        self,
        owner_id: UUID,
        owner_type: str,
        amount: Decimal,
        saga_id: str
    ) -> Dict[str, Any]:
        """
        Release reserved funds back to available balance.
        
        Used for compensation when saga fails.
        
        Args:
            owner_id: Wallet owner ID
            owner_type: organization, researcher, platform
            amount: Amount to release
            saga_id: Saga transaction ID
            
        Returns:
            Transaction result
        """
        wallet = self.get_or_create_wallet(owner_id, owner_type)
        
        balance_before = wallet.balance
        wallet.reserved_balance -= amount
        wallet.available_balance = wallet.balance - wallet.reserved_balance
        
        # Record transaction
        transaction = WalletTransaction(
            wallet_id=wallet.wallet_id,
            transaction_type="release",
            amount=amount,
            balance_before=balance_before,
            balance_after=wallet.balance,
            saga_id=saga_id,
            description=f"Released reserved {amount} {wallet.currency} (compensation)"
        )
        
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(wallet)
        
        return {
            "success": True,
            "wallet_id": str(wallet.wallet_id),
            "transaction_id": str(transaction.transaction_id),
            "released_amount": float(amount),
            "available_balance": float(wallet.available_balance)
        }
    
    def compensate_credit(
        self,
        owner_id: UUID,
        owner_type: str,
        amount: Decimal,
        saga_id: str
    ) -> Dict[str, Any]:
        """
        Compensate a credit transaction (remove funds).
        
        Used for rollback when saga fails.
        
        Args:
            owner_id: Wallet owner ID
            owner_type: organization, researcher, platform
            amount: Amount to remove
            saga_id: Saga transaction ID
            
        Returns:
            Transaction result
        """
        wallet = self.get_or_create_wallet(owner_id, owner_type)
        
        balance_before = wallet.balance
        wallet.balance -= amount
        wallet.available_balance = wallet.balance - wallet.reserved_balance
        
        # Record compensation transaction
        transaction = WalletTransaction(
            wallet_id=wallet.wallet_id,
            transaction_type="compensate",
            amount=amount,
            balance_before=balance_before,
            balance_after=wallet.balance,
            saga_id=saga_id,
            compensated=True,
            compensated_at=datetime.utcnow(),
            description=f"Compensated credit of {amount} {wallet.currency} (rollback)"
        )
        
        self.db.add(transaction)
        
        # Mark original transaction as compensated
        original_tx = self.db.query(WalletTransaction).filter(
            WalletTransaction.saga_id == saga_id,
            WalletTransaction.transaction_type == "credit",
            WalletTransaction.compensated == False
        ).first()
        
        if original_tx:
            original_tx.compensated = True
            original_tx.compensated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(wallet)
        
        return {
            "success": True,
            "wallet_id": str(wallet.wallet_id),
            "transaction_id": str(transaction.transaction_id),
            "compensated_amount": float(amount),
            "new_balance": float(wallet.balance)
        }
    
    def get_balance(self, owner_id: UUID, owner_type: str) -> Dict[str, Any]:
        """Get wallet balance."""
        wallet = self.get_or_create_wallet(owner_id, owner_type)
        
        return {
            "wallet_id": str(wallet.wallet_id),
            "balance": float(wallet.balance),
            "reserved_balance": float(wallet.reserved_balance),
            "available_balance": float(wallet.available_balance),
            "currency": wallet.currency
        }
    
    def get_transaction_history(
        self,
        owner_id: UUID,
        owner_type: str,
        limit: int = 50,
        offset: int = 0
    ) -> list:
        """Get wallet transaction history."""
        wallet = self.get_or_create_wallet(owner_id, owner_type)
        
        transactions = self.db.query(WalletTransaction).filter(
            WalletTransaction.wallet_id == wallet.wallet_id
        ).order_by(
            WalletTransaction.created_at.desc()
        ).limit(limit).offset(offset).all()
        
        return [
            {
                "transaction_id": str(tx.transaction_id),
                "transaction_type": tx.transaction_type,
                "amount": float(tx.amount),
                "balance_before": float(tx.balance_before),
                "balance_after": float(tx.balance_after),
                "description": tx.description,
                "created_at": tx.created_at.isoformat() if tx.created_at else None,
                "reference_type": tx.reference_type,
                "reference_id": str(tx.reference_id) if tx.reference_id else None,
                "saga_id": tx.saga_id,
                "compensated": tx.compensated,
                "status": "completed"
            }
            for tx in transactions
        ]
    
    def deduct_from_wallet(
        self,
        organization_id: UUID,
        amount: Decimal,
        description: str,
        reference_type: str = "subscription_payment",
        reference_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Deduct amount from organization wallet for subscription payment.
        
        Args:
            organization_id: Organization ID
            amount: Amount to deduct
            description: Transaction description
            reference_type: Type of reference
            reference_id: Reference ID
            
        Returns:
            Transaction result
        """
        wallet = self.get_or_create_wallet(organization_id, "organization")
        
        # Check available balance
        if wallet.available_balance < amount:
            raise ValueError(
                f"Insufficient wallet balance: available={wallet.available_balance}, required={amount}"
            )
        
        # Deduct from wallet
        balance_before = wallet.balance
        wallet.balance -= amount
        wallet.available_balance = wallet.balance - wallet.reserved_balance
        
        # Record transaction
        transaction = WalletTransaction(
            wallet_id=wallet.wallet_id,
            transaction_type="debit",
            amount=amount,
            balance_before=balance_before,
            balance_after=wallet.balance,
            reference_type=reference_type,
            reference_id=UUID(reference_id) if reference_id else None,
            saga_id=str(uuid4()),
            description=description
        )
        
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(wallet)
        
        return {
            "success": True,
            "wallet_id": str(wallet.wallet_id),
            "transaction_id": str(transaction.transaction_id),
            "debited_amount": float(amount),
            "new_balance": float(wallet.balance),
            "available_balance": float(wallet.available_balance)
        }
    
    def get_organization_wallet(self, organization_id: UUID) -> Wallet:
        """Get organization wallet."""
        return self.get_or_create_wallet(organization_id, "organization")
