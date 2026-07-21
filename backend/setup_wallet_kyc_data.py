#!/usr/bin/env python3
"""
Setup wallet and KYC test data for researcher.

This script:
1. Creates/updates wallet for researcher
2. Adds sample transactions
3. Creates KYC submission
4. Adds payment methods
"""
import sys
from decimal import Decimal
from uuid import uuid4

from sqlalchemy.orm import Session
from src.core.database import SessionLocal
from src.domain.models.user import User, UserRole
from src.domain.models.bounty_payment import Wallet, WalletTransaction
from src.domain.models.kyc import KYCVerification
from src.domain.models.payment_extended import PaymentMethod


def setup_wallet_and_kyc():
    """Setup wallet and KYC data for researcher@test.com"""
    db: Session = SessionLocal()
    
    try:
        # Find researcher user
        user = db.query(User).filter(
            User.email == "researcher@test.com"
        ).first()
        
        if not user:
            print("❌ Researcher user not found. Please create researcher@test.com first.")
            return False
        
        if not user.researcher:
            print("❌ User is not a researcher")
            return False
        
        researcher_id = user.researcher.id
        user_id = user.id
        print(f"✓ Found researcher: {user.email} (User ID: {user_id}, Researcher ID: {researcher_id})")
        
        # 1. Create/Update Wallet
        # Note: Wallet owner_id should reference users.id, not researchers.id
        wallet = db.query(Wallet).filter(
            Wallet.owner_id == user_id,
            Wallet.owner_type == "researcher"
        ).first()
        
        if not wallet:
            wallet = Wallet(
                owner_id=user_id,
                owner_type="researcher",
                currency="ETB",
                balance=Decimal("5000.00"),
                reserved_balance=Decimal("0.00"),
                available_balance=Decimal("5000.00")
            )
            db.add(wallet)
            db.flush()
            print(f"✓ Created wallet with 5000 ETB")
        else:
            wallet.balance = Decimal("5000.00")
            wallet.reserved_balance = Decimal("0.00")
            wallet.available_balance = Decimal("5000.00")
            print(f"✓ Updated wallet balance to 5000 ETB")
        
        # 2. Add sample transactions
        # Clear old transactions
        db.query(WalletTransaction).filter(
            WalletTransaction.wallet_id == wallet.wallet_id
        ).delete()
        
        transactions = [
            {
                "type": "credit",
                "amount": Decimal("1500.00"),
                "description": "Bounty payment for critical vulnerability",
                "balance_before": Decimal("0.00"),
                "balance_after": Decimal("1500.00")
            },
            {
                "type": "credit",
                "amount": Decimal("800.00"),
                "description": "Bounty payment for high severity issue",
                "balance_before": Decimal("1500.00"),
                "balance_after": Decimal("2300.00")
            },
            {
                "type": "credit",
                "amount": Decimal("2700.00"),
                "description": "Bounty payment for critical XSS vulnerability",
                "balance_before": Decimal("2300.00"),
                "balance_after": Decimal("5000.00")
            },
        ]
        
        for tx_data in transactions:
            tx = WalletTransaction(
                wallet_id=wallet.wallet_id,
                transaction_type=tx_data["type"],
                amount=tx_data["amount"],
                balance_before=tx_data["balance_before"],
                balance_after=tx_data["balance_after"],
                description=tx_data["description"],
                saga_id=str(uuid4())
            )
            db.add(tx)
        
        print(f"✓ Added {len(transactions)} sample transactions")
        
        # 3. Create KYC Verification
        kyc = db.query(KYCVerification).filter(
            KYCVerification.user_id == user.id
        ).first()
        
        if not kyc:
            kyc = KYCVerification(
                user_id=user.id,
                status="pending"
            )
            db.add(kyc)
            db.flush()
            print(f"✓ Created KYC verification (status: pending)")
        else:
            print(f"✓ KYC verification exists (status: {kyc.status})")
        
        # 4. Add payment method
        payment_method = db.query(PaymentMethod).filter(
            PaymentMethod.user_id == user.id
        ).first()
        
        if not payment_method:
            payment_method = PaymentMethod(
                user_id=user.id,
                method_type="bank_transfer",
                bank_name="Commercial Bank of Ethiopia",
                account_number="1234567890",
                account_name=user.email.split('@')[0].title(),
                is_default=True,
                is_verified=False
            )
            db.add(payment_method)
            print(f"✓ Added bank transfer payment method")
        else:
            print(f"✓ Payment method exists ({payment_method.method_type})")
        
        db.commit()
        print("\n✅ Successfully set up wallet and KYC data!")
        print(f"\nWallet Summary:")
        print(f"  Balance: {wallet.balance} ETB")
        print(f"  Reserved: {wallet.reserved_balance} ETB")
        print(f"  Available: {wallet.available_balance} ETB")
        print(f"  Transactions: {len(transactions)}")
        
        return True
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    success = setup_wallet_and_kyc()
    sys.exit(0 if success else 1)
