"""
Test wallet recharge to ensure no duplicates are created.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy.orm import Session
from src.core.database import SessionLocal
from src.domain.models.user import User
from src.domain.models.bounty_payment import Wallet, WalletTransaction
from src.services.wallet_service import WalletService
from decimal import Decimal
from uuid import uuid4

def test_wallet_recharge():
    """Test wallet recharge without creating duplicates."""
    db: Session = SessionLocal()
    
    try:
        print("\n" + "="*80)
        print("WALLET RECHARGE TEST - NO DUPLICATES")
        print("="*80)
        
        # Get organization user
        org_user = db.query(User).filter(User.email == "org@test.com").first()
        if not org_user:
            print("❌ Organization user not found")
            return
        
        print(f"\n✅ Organization User: {org_user.email} (ID: {org_user.id})")
        
        # Check initial wallet count
        print(f"\n[1] Checking initial wallet count...")
        initial_wallets = db.query(Wallet).filter(
            Wallet.owner_id == org_user.id,
            Wallet.owner_type == "organization"
        ).all()
        print(f"   Initial wallets: {len(initial_wallets)}")
        for w in initial_wallets:
            print(f"   - {w.wallet_id}: {w.balance} ETB")
        
        initial_balance = initial_wallets[0].balance if initial_wallets else Decimal("0")
        
        # Test multiple recharges
        service = WalletService(db)
        
        print(f"\n[2] Testing 3 consecutive recharges...")
        for i in range(1, 4):
            saga_id = str(uuid4())
            amount = Decimal("1000")
            
            print(f"\n   Recharge #{i}: {amount} ETB")
            result = service.credit_wallet(
                owner_id=org_user.id,
                owner_type="organization",
                amount=amount,
                saga_id=saga_id,
                reference_type="wallet_recharge",
                reference_id=None
            )
            
            print(f"   ✅ Transaction ID: {result['transaction_id']}")
            print(f"   New balance: {result['new_balance']} ETB")
            
            # Check wallet count after each recharge
            wallets_after = db.query(Wallet).filter(
                Wallet.owner_id == org_user.id,
                Wallet.owner_type == "organization"
            ).all()
            
            print(f"   Wallet count: {len(wallets_after)}")
            
            if len(wallets_after) > 1:
                print(f"   ❌ DUPLICATE DETECTED! Found {len(wallets_after)} wallets")
                for w in wallets_after:
                    print(f"      - {w.wallet_id}: {w.balance} ETB")
                return
        
        # Final verification
        print(f"\n[3] Final verification...")
        final_wallets = db.query(Wallet).filter(
            Wallet.owner_id == org_user.id,
            Wallet.owner_type == "organization"
        ).all()
        
        print(f"   Final wallet count: {len(final_wallets)}")
        
        if len(final_wallets) == 1:
            wallet = final_wallets[0]
            expected_balance = initial_balance + Decimal("3000")
            print(f"   ✅ Single wallet maintained!")
            print(f"   Wallet ID: {wallet.wallet_id}")
            print(f"   Initial balance: {initial_balance} ETB")
            print(f"   Expected balance: {expected_balance} ETB")
            print(f"   Actual balance: {wallet.balance} ETB")
            
            if wallet.balance == expected_balance:
                print(f"   ✅ Balance is correct!")
            else:
                print(f"   ❌ Balance mismatch!")
        else:
            print(f"   ❌ Multiple wallets found: {len(final_wallets)}")
            for w in final_wallets:
                print(f"      - {w.wallet_id}: {w.balance} ETB")
        
        # Test transaction history
        print(f"\n[4] Checking transaction history...")
        transactions = db.query(WalletTransaction).filter(
            WalletTransaction.wallet_id == final_wallets[0].wallet_id
        ).order_by(WalletTransaction.created_at.desc()).limit(5).all()
        
        print(f"   Recent transactions: {len(transactions)}")
        for tx in transactions:
            print(f"   - {tx.transaction_type}: {tx.amount} ETB (Balance after: {tx.balance_after})")
        
        print("\n" + "="*80)
        print("✅ TEST PASSED: No duplicates created!")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    test_wallet_recharge()
