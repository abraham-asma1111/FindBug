"""
Check wallet balance for organization user.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy.orm import Session
from src.core.database import SessionLocal
from src.domain.models.user import User
from src.domain.models.bounty_payment import Wallet, WalletTransaction

def check_wallet():
    """Check wallet balance."""
    db: Session = SessionLocal()
    
    try:
        print("\n" + "="*80)
        print("WALLET BALANCE CHECK")
        print("="*80)
        
        # Get organization user
        org_user = db.query(User).filter(User.email == "org@test.com").first()
        if not org_user:
            print("❌ Organization user not found")
            return
        
        print(f"\n✅ Organization User:")
        print(f"   Email: {org_user.email}")
        print(f"   User ID: {org_user.id}")
        print(f"   Role: {org_user.role}")
        
        # Check all wallets for this user
        print(f"\n📊 Checking wallets for user_id={org_user.id}...")
        wallets = db.query(Wallet).filter(Wallet.owner_id == org_user.id).all()
        
        if not wallets:
            print("   ❌ No wallets found for this user")
        else:
            print(f"   ✅ Found {len(wallets)} wallet(s):")
            for wallet in wallets:
                print(f"\n   Wallet ID: {wallet.wallet_id}")
                print(f"   Owner Type: {wallet.owner_type}")
                print(f"   Balance: {wallet.balance} {wallet.currency}")
                print(f"   Available: {wallet.available_balance} {wallet.currency}")
                print(f"   Reserved: {wallet.reserved_balance} {wallet.currency}")
                print(f"   Created: {wallet.created_at}")
                
                # Get transactions for this wallet
                transactions = db.query(WalletTransaction).filter(
                    WalletTransaction.wallet_id == wallet.wallet_id
                ).order_by(WalletTransaction.created_at.desc()).limit(10).all()
                
                if transactions:
                    print(f"\n   Recent Transactions ({len(transactions)}):")
                    for tx in transactions:
                        print(f"      - {tx.transaction_type}: {tx.amount} {wallet.currency}")
                        print(f"        Balance After: {tx.balance_after}")
                        print(f"        Reference: {tx.reference_type}")
                        print(f"        Created: {tx.created_at}")
                else:
                    print(f"\n   No transactions found")
        
        # Check all wallets in database
        print(f"\n📊 All wallets in database:")
        all_wallets = db.query(Wallet).all()
        print(f"   Total wallets: {len(all_wallets)}")
        for w in all_wallets:
            print(f"   - Owner ID: {w.owner_id}, Type: {w.owner_type}, Balance: {w.balance}")
        
        print("\n" + "="*80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_wallet()
